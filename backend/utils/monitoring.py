"""
Monitoring & Observability Utilities
Health checks, metrics collection, and error tracking
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify, request
import time

# Optional psutil import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Service for system health monitoring"""
    
    def __init__(self, app=None):
        self.app = app
        self.start_time = datetime.utcnow()
        
    def check_database(self) -> Dict[str, Any]:
        """Check MongoDB connection health"""
        try:
            from backend.models.database import get_db
            db = get_db()
            # Ping database
            db.command('ping')
            return {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        try:
            from backend.workers.queue_manager import queue_manager
            if queue_manager.is_available():
                stats = queue_manager.get_queue_stats()
                return {
                    'status': 'healthy',
                    'message': 'Redis connection successful',
                    'queues': stats
                }
            else:
                return {
                    'status': 'unavailable',
                    'message': 'Redis not configured or unavailable'
                }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        if not PSUTIL_AVAILABLE:
            return {
                'status': 'unavailable',
                'message': 'psutil not installed - system monitoring disabled'
            }
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = 'healthy'
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = 'warning'
            
            return {
                'status': status,
                'cpu_usage': f"{cpu_percent}%",
                'memory_usage': f"{memory.percent}%",
                'memory_available': f"{memory.available / (1024**3):.2f} GB",
                'disk_usage': f"{disk.percent}%",
                'disk_free': f"{disk.free / (1024**3):.2f} GB"
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                'status': 'unknown',
                'message': str(e)
            }
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get application uptime"""
        uptime = datetime.utcnow() - self.start_time
        return {
            'started_at': self.start_time.isoformat(),
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime).split('.')[0]
        }
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'operational',
            'uptime': self.get_uptime(),
            'checks': {
                'database': self.check_database(),
                'redis': self.check_redis(),
                'system': self.check_system_resources()
            }
        }


class MetricsCollector:
    """Collect and expose application metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_by_endpoint': {},
            'requests_by_status': {},
            'response_times': [],
            'errors_total': 0
        }
    
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        """Record request metrics"""
        self.metrics['requests_total'] += 1
        
        # By endpoint
        if endpoint not in self.metrics['requests_by_endpoint']:
            self.metrics['requests_by_endpoint'][endpoint] = 0
        self.metrics['requests_by_endpoint'][endpoint] += 1
        
        # By status code
        status_group = f"{status_code // 100}xx"
        if status_group not in self.metrics['requests_by_status']:
            self.metrics['requests_by_status'][status_group] = 0
        self.metrics['requests_by_status'][status_group] += 1
        
        # Response time
        self.metrics['response_times'].append(response_time)
        if len(self.metrics['response_times']) > 1000:  # Keep last 1000
            self.metrics['response_times'].pop(0)
        
        # Errors
        if status_code >= 400:
            self.metrics['errors_total'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        return {
            'total_requests': self.metrics['requests_total'],
            'total_errors': self.metrics['errors_total'],
            'error_rate': f"{(self.metrics['errors_total'] / max(self.metrics['requests_total'], 1) * 100):.2f}%",
            'avg_response_time_ms': f"{avg_response_time:.2f}",
            'requests_by_endpoint': self.metrics['requests_by_endpoint'],
            'requests_by_status': self.metrics['requests_by_status']
        }


class ErrorTracker:
    """Track and log errors for debugging"""
    
    def __init__(self):
        self.sentry_enabled = os.getenv('SENTRY_DSN') is not None
        if self.sentry_enabled:
            try:
                import sentry_sdk
                sentry_sdk.init(
                    dsn=os.getenv('SENTRY_DSN'),
                    traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
                    environment=os.getenv('ENVIRONMENT', 'development')
                )
                logger.info("✅ Sentry error tracking initialized")
            except ImportError:
                logger.warning("⚠️ sentry-sdk not installed. Install with: pip install sentry-sdk")
                self.sentry_enabled = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize Sentry: {e}")
                self.sentry_enabled = False
    
    def capture_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Capture exception with context"""
        if self.sentry_enabled:
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    if context:
                        for key, value in context.items():
                            scope.set_context(key, value)
                    sentry_sdk.capture_exception(exception)
            except Exception as e:
                logger.error(f"Failed to capture exception in Sentry: {e}")
        
        # Always log locally
        logger.error(f"Exception occurred: {exception}", exc_info=True, extra=context or {})
    
    def capture_message(self, message: str, level: str = 'info', context: Optional[Dict[str, Any]] = None):
        """Capture message with context"""
        if self.sentry_enabled:
            try:
                import sentry_sdk
                with sentry_sdk.push_scope() as scope:
                    if context:
                        for key, value in context.items():
                            scope.set_context(key, value)
                    sentry_sdk.capture_message(message, level=level)
            except Exception as e:
                logger.error(f"Failed to capture message in Sentry: {e}")
        
        # Always log locally
        log_func = getattr(logger, level, logger.info)
        log_func(message, extra=context or {})


# Global instances
health_check_service = HealthCheckService()
metrics_collector = MetricsCollector()
error_tracker = ErrorTracker()


def setup_monitoring_routes(app):
    """Setup monitoring endpoints"""
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        result = health_check_service.comprehensive_health_check()
        
        # Determine HTTP status based on checks
        all_healthy = all(
            check.get('status') in ['healthy', 'unavailable']  # unavailable is ok for optional services
            for check in result['checks'].values()
        )
        
        status_code = 200 if all_healthy else 503
        return jsonify(result), status_code
    
    @app.route('/metrics', methods=['GET'])
    def get_metrics():
        """Metrics endpoint (Prometheus-compatible format could be added)"""
        return jsonify(metrics_collector.get_metrics()), 200
    
    @app.route('/health/ready', methods=['GET'])
    def readiness_check():
        """Kubernetes readiness probe"""
        db_check = health_check_service.check_database()
        if db_check['status'] == 'healthy':
            return jsonify({'status': 'ready'}), 200
        return jsonify({'status': 'not ready', 'reason': db_check.get('message')}), 503
    
    @app.route('/health/live', methods=['GET'])
    def liveness_check():
        """Kubernetes liveness probe"""
        return jsonify({'status': 'alive'}), 200
    
    logger.info("✅ Monitoring routes registered: /health, /metrics, /health/ready, /health/live")


def setup_request_tracking(app):
    """Setup request/response tracking middleware"""
    
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            response_time = (time.time() - request.start_time) * 1000  # ms
            endpoint = request.endpoint or request.path
            metrics_collector.record_request(
                endpoint=endpoint,
                status_code=response.status_code,
                response_time=response_time
            )
        return response
    
    logger.info("✅ Request tracking middleware enabled")


def setup_error_handlers(app):
    """Setup global error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        error_tracker.capture_exception(error, context={
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url
        })
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        error_tracker.capture_exception(error, context={
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url
        })
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    logger.info("✅ Error handlers registered")


def initialize_monitoring(app):
    """Initialize all monitoring features"""
    setup_monitoring_routes(app)
    setup_request_tracking(app)
    setup_error_handlers(app)
    logger.info("🔍 Monitoring & Observability initialized")
