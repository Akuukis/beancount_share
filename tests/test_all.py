from pytest_bdd import scenarios

import conftest

scenarios('features/basics.feature')
scenarios('features/one-to-one.feature')
scenarios('features/one-to-many.feature')
scenarios('features/many-to-many.feature')
scenarios('features/shortcuts.feature')
scenarios('features/currencies.feature')
scenarios('features/errors.feature')
scenarios('features/usecases.feature')
