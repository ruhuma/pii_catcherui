from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dbcat.api import open_catalog, add_mysql_source
from piicatcher.api import scan_database, OutputFormat
from typing import List, Dict
from pydantic import BaseModel

app = FastAPI()


class DatabaseItem(BaseModel):
    database: str
    table: str
    field: str
    PIILevel: str
    Class: str

class ScanSettings(BaseModel):
    include_schema_regex: list = ["^crm$"]
    exclude_schema_regex: list =  ["^salika$", "^world$"]

@app.post("/scan",response_model=List[DatabaseItem])
async def scan_database_endpoint(settings: ScanSettings):
    # Open the catalog
    catalog = open_catalog(app_dir='/tmp/.config/piicatcher', path=':memory:', secret='my_secret')
    with catalog.managed_session:
        # Add the MySQL source
        source = add_mysql_source(
            catalog=catalog,
            name="mysql_db",
            uri="127.0.0.1",
            username="root",
            password="root",
            database="crm"
        )
        # Perform the scan using hardcoded regex patterns
        output = scan_database(
            catalog=catalog,
            source=source,
            include_schema_regex=settings.include_schema_regex,
            exclude_schema_regex=settings.exclude_schema_regex,
            output_format=OutputFormat.tabular  # Assuming tabular output can be converted to JSON-like structure
        )
        #return output

   # print(output)

    return [DatabaseItem(database=item[0], table=item[1], field=item[2], PIILevel=item[3], Class=item[4]) for item in output]
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)