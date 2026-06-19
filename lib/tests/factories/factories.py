import hashlib

import factory
from lib.tests.factories.base import AsyncFactory, BaseModelFactory, TimeStampMixinFactory
from lib.utils.events.event_types import EventProcessingState, EventType
from lib.utils.models import Product, Purchase, User, UserResource
from lib.utils.models.events import Event, EventLog
from lib.utils.schemas.events import EventMessage
from lib.utils.schemas.game import ResourceType
from lib.utils.schemas.products import ProductType, PurchaseStatus
from lib.utils.schemas.users import UserRole


class EventMessageFactory(AsyncFactory):
    class Meta:
        model = EventMessage

    event_type = EventType.EVENT_1
    payload = factory.LazyFunction(dict)


class UserFactory(BaseModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    username = factory.Faker("user_name")
    password = factory.LazyAttribute(lambda obj: hashlib.sha256(f"password_{obj.username}".encode()).hexdigest())
    is_active = True
    role = UserRole.PLAYER
    email_verified = True


class UserResourceFactory(BaseModelFactory):
    class Meta:
        model = UserResource

    id = factory.SubFactory(UserFactory)
    scraps = 1000
    raw_bronze = 0
    raw_silver = 0
    raw_gold = 0
    bronze_ingots = 0
    silver_ingots = 0
    gold_ingots = 0
    crops = 1000
    wood = 1000
    silk = 0
    kegs = 3
    big_kegs = 1
    chests = 0
    keys = 3
    rare_gem = 0
    money = 2000
    flowers = 0
    first_aid_kits = 0
    shields = 0
    immune_magics = 0


class ProductFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = Product

    title = "title"
    is_active = True
    type = ProductType.RESOURCE
    priority = 999
    price = 100.43
    data = {
        "resources": {
            ResourceType.MONEY: 2000,
            ResourceType.WOOD: 1000,
            ResourceType.SCRAPS: 1500,
        },
    }


class PurchaseFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = Purchase

    user_id = factory.SubFactory(UserFactory)
    product_id = factory.SubFactory(ProductFactory)
    status = PurchaseStatus.PENDING
    amount = 0
    transaction_id = None
    response_description = None


class EventFactory(BaseModelFactory):
    class Meta:
        model = Event

    type = EventType.EVENT_1
    processing = factory.LazyFunction(list)


class EventLogFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = EventLog

    type = EventType.EVENT_1
    state = EventProcessingState.SENT
    payload = factory.LazyFunction(dict)
    actions_log = factory.LazyFunction(list)
    retry_count = 0
    dedup_key = None
