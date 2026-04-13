from pydantic import AliasGenerator, ConfigDict
from pydantic.alias_generators import to_pascal, to_snake

kobo_api_alias = AliasGenerator(
    serialization_alias=to_pascal,
    validation_alias=to_snake,
)


config = ConfigDict(
    alias_generator=kobo_api_alias,
)
