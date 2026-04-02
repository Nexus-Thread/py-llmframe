#!/bin/bash

if [ "$1" = "init" ]; then
  git remote add clinerules https://github.com/ondrej-winter/clinerules
  git fetch clinerules split-python-hexagonal-agents split-python-hexagonal-clinerules
  git subtree add --prefix=.agents clinerules split-python-hexagonal-agents --squash
  git subtree add --prefix=.clinerules clinerules split-python-hexagonal-clinerules --squash
else
  git fetch clinerules split-python-hexagonal-agents split-python-hexagonal-clinerules
  git subtree pull --prefix=.agents clinerules split-python-hexagonal-agents --squash
  git subtree pull --prefix=.clinerules clinerules split-python-hexagonal-clinerules --squash
fi
