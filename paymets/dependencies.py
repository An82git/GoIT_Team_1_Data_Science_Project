from typing import Annotated
from fastapi import Depends
from paymets.controllers import PaymentsController

PaymentsControllerDep = Annotated[PaymentsController, Depends(PaymentsController)]