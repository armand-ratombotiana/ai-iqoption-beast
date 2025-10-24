"""Flask application factory"""

from flask import Flask

# Handle both package and standalone imports
try:
    from ..utils.config import Config
    from ..utils.logger import setup_logger
except ImportError:
    from utils.config import Config
    from utils.logger import setup_logger


def create_app(config: Config = None) -> Flask:
    """
    Create and configure Flask application

    Args:
        config: Configuration object

    Returns:
        Configured Flask app
    """
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = Config()

    app.config['TRADING_CONFIG'] = config

    # Setup logger
    logger = setup_logger()
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)

    # Register blueprints
    from .routes import trading_bp
    app.register_blueprint(trading_bp)

    # Display configuration
    config.display()

    return app
