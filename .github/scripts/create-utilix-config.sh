#!/bin/bash

cat > $HOME/.xenon_config <<EOF
[RunDB]
rundb_api_url = $RUNDB_API_URL
rundb_api_user = $RUNDB_API_USER
rundb_api_password = $RUNDB_API_PASSWORD
pymongo_url = $PYMONGO_URL
pymongo_user = $PYMONGO_USER
pymongo_password = $PYMONGO_PASSWORD
pymongo_database = $PYMONGO_DATABASE
EOF

