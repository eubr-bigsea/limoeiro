import os
from pgqueuer.__main__ import main
import dotenv

dotenv.load_dotenv()

if __name__ == "__main__":
    os.environ["PGDSN"] = os.environ["DB_URL"].replace("+asyncpg", "")
    main()
