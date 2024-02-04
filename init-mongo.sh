mongosh -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin <<EOF
    db = db.getSiblingDB('$MONGO_INITDB_DATABASE');
    db.createUser({
        user: '$MONGO_INITDB_USER_USERNAME', 
        pwd: '$MONGO_INITDB_USER_PASSWORD', 
        roles: [{
            role: 'readWrite', 
            db: '$MONGO_INITDB_DATABASE'
        }]
    });
    db.getUsers()
    
EOF
