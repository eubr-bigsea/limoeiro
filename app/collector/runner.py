import argparse
from dotenv import load_dotenv

from app.collector.data_collection_engine import DataCollectionEngine
import logging

from app.collector.utils.api_client import DatabaseProviderApiClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Executa a ingestão para um provedor de banco de dados"
    )
    parser.add_argument(
        "--id",
        type=str,
        required=True,
        help="ID do provedor de banco de dados (required)",
    )
    args = parser.parse_args()

    provider_client = DatabaseProviderApiClient()
    logger.info("Iniciando consulta ao provedor de banco de dados %s", args.id)
    provider = provider_client.get(args.id)
    ingestions = provider_client.get_ingestions(args.id)
    connections = provider_client.get_connections(args.id)

    logger.info("Existe(m) %s ingestão(ões) configurada(s).", len(ingestions))
    logger.info("Existe(m) %s conexão(ões) configurada(s).", len(connections))

    engine = DataCollectionEngine()
    engine._execute_collection(provider, connections[0], ingestions[0])


if __name__ == "__main__":
    main()
