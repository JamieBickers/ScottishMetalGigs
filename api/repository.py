import os

from azure.cosmos import CosmosClient

class Repository:
    ENDPOINT = os.environ["COSMOS_ENDPOINT"]
    KEY = os.environ["COSMOS_KEY"]
    DATABASE_NAME = "scottishmetalgigs"
    GIGS_CONTAINER_NAME = "gigs"

    def __init__(self):
        client = CosmosClient(url=self.ENDPOINT, credential=self.KEY)
        database = client.get_database_client(self.DATABASE_NAME)
        self.container = database.get_container_client(self.GIGS_CONTAINER_NAME)

    def get_gigs(self):
        QUERY = f"SELECT * FROM {self.GIGS_CONTAINER_NAME}"
        results = self.container.query_items(
            query=QUERY, enable_cross_partition_query=True
        )

        return list(results)

    def save_gigs(self, gigs):
        for gig in gigs:
            self.container.create_item(gig.as_serialisable(), enable_automatic_id_generation=True)