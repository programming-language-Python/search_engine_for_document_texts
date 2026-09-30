from api.document import router as router_documents
from api.elasticsearch import router as router_elasticsearch

all_routers = [
    router_documents,
    router_elasticsearch,
]
