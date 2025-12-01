# /app/extensions.py

from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Instantiate the Marshmallow library
ma = Marshmallow()

# creating an instance of Limiter & a default rate limit
limiter = Limiter(
    get_remote_address,
    default_limits = ['200 per day', '50 per hour']
    ) 

cache = Cache()