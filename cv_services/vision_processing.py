"""
Computer Vision Processing Module
Implements shelf intelligence, product detection, and planogram compliance
"""

import cv2
import numpy as np
from PIL import Image
from typing import List, Dict, Tuple, Optional
import io
import base64

# Deep Learning
try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models.detection import fasterrcnn_resnet50_fpn
    TORCH_AVAILABLE = True
except (ImportError, OSError) as e:
    # OSError can occur on Windows with DLL initialization issues
    print(f"PyTorch not available: {e}")
    TORCH_AVAILABLE = False
    torch = None

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"YOLO not available: {e}")
    YOLO_AVAILABLE = False
    YOLO = None


class ShelfDetector:
    """
    Detect products, empty shelves, and misplaced items using computer vision
    """
    
    def __init__(self, model_type='yolo'):
        """
        Initialize detector
        
        Args:
            model_type: 'yolo', 'faster_rcnn', or 'custom'
        """
        self.model_type = model_type
        self.model = None
        self.class_names = []
        
    def load_model(self, model_path: Optional[str] = None):
        """Load pre-trained or custom detection model"""
        if self.model_type == 'yolo' and YOLO_AVAILABLE:
            if model_path:
                self.model = YOLO(model_path)
            else:
                # Use pre-trained YOLO model
                self.model = YOLO('yolov8n.pt')
                
        elif self.model_type == 'faster_rcnn' and TORCH_AVAILABLE:
            self.model = fasterrcnn_resnet50_fpn(pretrained=True)
            self.model.eval()
            
        else:
            print(f"Warning: {self.model_type} not available, using fallback")
            
    def preprocess_image(self, image_data) -> np.ndarray:
        """
        Preprocess image for detection
        
        Args:
            image_data: PIL Image, numpy array, or file path
            
        Returns:
            Preprocessed image array
        """
        if isinstance(image_data, str):
            image = cv2.imread(image_data)
        elif isinstance(image_data, Image.Image):
            image = np.array(image_data)
        else:
            image = image_data
            
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        return image
        
    def detect_products(self, image: np.ndarray, confidence_threshold=0.5) -> List[Dict]:
        """
        Detect products in shelf image
        
        Returns:
            List of detections with bbox, confidence, class
        """
        detections = []
        
        if self.model_type == 'yolo' and self.model:
            results = self.model(image, conf=confidence_threshold)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    
                    detections.append({
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': conf,
                        'class_id': cls,
                        'class_name': self.model.names[cls] if hasattr(self.model, 'names') else f'class_{cls}'
                    })
                    
        elif self.model_type == 'faster_rcnn' and self.model:
            # Convert to tensor
            transform = transforms.ToTensor()
            image_tensor = transform(image).unsqueeze(0)
            
            with torch.no_grad():
                predictions = self.model(image_tensor)[0]
                
            for i, score in enumerate(predictions['scores']):
                if score >= confidence_threshold:
                    box = predictions['boxes'][i].cpu().numpy()
                    label = int(predictions['labels'][i])
                    
                    detections.append({
                        'bbox': box.tolist(),
                        'confidence': float(score),
                        'class_id': label,
                        'class_name': f'class_{label}'
                    })
                    
        return detections
        
    def detect_empty_shelves(self, image: np.ndarray, grid_size=(5, 10)) -> List[Dict]:
        """
        Detect empty shelf sections using grid analysis
        
        Args:
            image: Shelf image
            grid_size: (rows, cols) for shelf grid
            
        Returns:
            List of empty shelf sections
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        h, w = gray.shape
        rows, cols = grid_size
        
        cell_h = h // rows
        cell_w = w // cols
        
        empty_sections = []
        
        for i in range(rows):
            for j in range(cols):
                # Extract cell
                y1, y2 = i * cell_h, (i + 1) * cell_h
                x1, x2 = j * cell_w, (j + 1) * cell_w
                cell = gray[y1:y2, x1:x2]
                
                # Calculate cell features
                mean_intensity = np.mean(cell)
                std_intensity = np.std(cell)
                edge_density = cv2.Canny(cell, 50, 150).sum() / (cell_h * cell_w)
                
                # Empty shelf heuristic: high intensity, low variance, low edges
                is_empty = (mean_intensity > 200 and std_intensity < 20) or edge_density < 0.01
                
                if is_empty:
                    empty_sections.append({
                        'row': i,
                        'col': j,
                        'bbox': [x1, y1, x2, y2],
                        'confidence': min(1.0, mean_intensity / 255.0)
                    })
                    
        return empty_sections
        
    def check_planogram_compliance(self, 
                                   detected_products: List[Dict], 
                                   planogram: Dict) -> Dict:
        """
        Check if shelf layout matches planogram
        
        Args:
            detected_products: List of detected products
            planogram: Expected product layout
            
        Returns:
            Compliance report
        """
        compliance_score = 0.0
        misplaced_products = []
        missing_products = []
        
        expected_positions = planogram.get('positions', [])
        
        # Simple position-based matching
        for expected in expected_positions:
            exp_bbox = expected['bbox']
            exp_product = expected['product_id']
            
            # Find closest detection
            found = False
            for detection in detected_products:
                det_bbox = detection['bbox']
                
                # Calculate IoU (Intersection over Union)
                iou = self._calculate_iou(exp_bbox, det_bbox)
                
                if iou > 0.3 and detection.get('product_id') == exp_product:
                    found = True
                    compliance_score += 1
                    break
                elif iou > 0.3 and detection.get('product_id') != exp_product:
                    misplaced_products.append({
                        'expected': exp_product,
                        'actual': detection.get('product_id'),
                        'position': det_bbox
                    })
                    
            if not found:
                missing_products.append(expected)
                
        # Calculate overall compliance
        if len(expected_positions) > 0:
            compliance_score = (compliance_score / len(expected_positions)) * 100
        else:
            compliance_score = 100.0
            
        return {
            'compliance_score': compliance_score,
            'misplaced_count': len(misplaced_products),
            'missing_count': len(missing_products),
            'misplaced_products': misplaced_products,
            'missing_products': missing_products
        }
        
    def _calculate_iou(self, box1: List[float], box2: List[float]) -> float:
        """Calculate Intersection over Union between two boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
            
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Union
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0


class ProductRecognizer:
    """Train and use product recognition models"""
    
    def __init__(self):
        self.model = None
        self.product_encodings = {}
        
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """Extract visual features from product image"""
        # Resize to standard size
        image = cv2.resize(image, (224, 224))
        
        # Extract color histogram
        hist_b = cv2.calcHist([image], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([image], [1], None, [32], [0, 256])
        hist_r = cv2.calcHist([image], [2], None, [32], [0, 256])
        
        # Extract edge features
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_features = np.array([edges.sum(), edges.mean(), edges.std()])
        
        # Combine features
        features = np.concatenate([
            hist_b.flatten(),
            hist_g.flatten(),
            hist_r.flatten(),
            edge_features
        ])
        
        return features / (np.linalg.norm(features) + 1e-10)  # Normalize
        
    def train(self, training_images: Dict[int, List[np.ndarray]]):
        """
        Train product recognizer
        
        Args:
            training_images: Dict mapping product_id to list of training images
        """
        for product_id, images in training_images.items():
            encodings = [self.extract_features(img) for img in images]
            self.product_encodings[product_id] = np.mean(encodings, axis=0)
            
    def recognize(self, image: np.ndarray, threshold=0.7) -> Optional[int]:
        """
        Recognize product in image
        
        Returns:
            product_id if recognized, None otherwise
        """
        features = self.extract_features(image)
        
        best_match = None
        best_similarity = 0.0
        
        for product_id, encoding in self.product_encodings.items():
            # Cosine similarity
            similarity = np.dot(features, encoding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = product_id
                
        if best_similarity >= threshold:
            return best_match
        return None


class ImagePreprocessor:
    """Image preprocessing utilities for CV pipeline"""
    
    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """Enhance image contrast"""
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        return cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
    @staticmethod
    def correct_perspective(image: np.ndarray, corners: List[Tuple[int, int]]) -> np.ndarray:
        """Correct shelf perspective distortion"""
        if len(corners) != 4:
            return image
            
        # Order points: top-left, top-right, bottom-right, bottom-left
        pts = np.array(corners, dtype=np.float32)
        
        # Calculate target dimensions
        width = max(
            np.linalg.norm(pts[0] - pts[1]),
            np.linalg.norm(pts[2] - pts[3])
        )
        height = max(
            np.linalg.norm(pts[0] - pts[3]),
            np.linalg.norm(pts[1] - pts[2])
        )
        
        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype=np.float32)
        
        matrix = cv2.getPerspectiveTransform(pts, dst)
        return cv2.warpPerspective(image, matrix, (int(width), int(height)))
        
    @staticmethod
    def segment_products(image: np.ndarray) -> List[np.ndarray]:
        """Segment individual products from shelf image"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        products = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small regions
                x, y, w, h = cv2.boundingRect(contour)
                product = image[y:y+h, x:x+w]
                products.append(product)
                
        return products
