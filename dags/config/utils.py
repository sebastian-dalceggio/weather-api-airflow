"Util classes and methods"

from dataclasses import dataclass

import pendulum


@dataclass
class QueryData:
    """Data of queries"""

    query: str
    start_date: pendulum.DateTime
    end_date: pendulum.DateTime
