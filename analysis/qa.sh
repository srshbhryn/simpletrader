
CHECK='simpletrader'
IGNORE='*migrations*,*indices*'
IGNORE_REGEX='.*migrations.*,.*indices.*'

pycodestyle --exclude=$IGNORE --format=pylint $CHECK && \
pylint --load-plugins pylint_django --django-settings-module=simpletrader.settings \
    --ignore-paths= $CHECK
