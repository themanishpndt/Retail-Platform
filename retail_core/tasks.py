from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_demand_forecasting():
    """Run demand forecasting for all products."""
    from ml_services.models import ForecastModel, DemandForecastingResult
    from products.models import Product
    from inventory.models import Store
    
    logger.info("Starting demand forecasting task...")
    
    try:
        # Get active models
        models = ForecastModel.objects.filter(is_active=True)
        
        if not models.exists():
            logger.warning("No active forecasting models found")
            return
        
        # TODO: Implement forecasting logic here
        logger.info(f"Forecasting completed with {models.count()} models")
    
    except Exception as e:
        logger.error(f"Error in demand forecasting: {str(e)}")
        raise


@shared_task
def process_batch_inventory_update(updates):
    """Process batch inventory updates."""
    from inventory.models import InventoryLevel, InventoryTransaction
    
    logger.info(f"Processing {len(updates)} inventory updates...")
    
    try:
        for update in updates:
            try:
                inv_level = InventoryLevel.objects.get(id=update['inventory_level_id'])
                
                # Create transaction
                InventoryTransaction.objects.create(
                    inventory_level=inv_level,
                    transaction_type=update.get('type', 'ADJUST'),
                    quantity_change=update.get('quantity_change', 0),
                    reference_doc=update.get('reference', ''),
                    notes=update.get('notes', ''),
                    performed_by=update.get('performed_by', 'SYSTEM'),
                )
                
                logger.info(f"Updated inventory level {inv_level.id}")
            
            except Exception as e:
                logger.error(f"Error updating inventory: {str(e)}")
        
        logger.info("Batch inventory update completed")
    
    except Exception as e:
        logger.error(f"Error in batch inventory update: {str(e)}")
        raise


@shared_task
def sync_external_data_source(source_id):
    """Sync data from external source."""
    from data_ingestion.models import DataSource, DataIngestionJob
    
    logger.info(f"Syncing data from source {source_id}...")
    
    try:
        source = DataSource.objects.get(id=source_id)
        
        # TODO: Implement data sync logic based on source type
        logger.info(f"Data sync completed for {source.name}")
    
    except DataSource.DoesNotExist:
        logger.error(f"Data source {source_id} not found")
    except Exception as e:
        logger.error(f"Error syncing data: {str(e)}")
        raise
