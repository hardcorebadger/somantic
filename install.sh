

if [ -z "$1" ] 
then
    echo "[Somantic] Installing everything....";
    # install app
    cd app;
    npm install;
    cd ..;
    # install functions
    cd functions;
    python3.11 -m venv venv;              
    source venv/bin/activate;
    pip3 install --upgrade pip;
    python3.11 -m pip install -r requirements.txt;
fi

# install the app
if [ "$1" = "app" ] 
then
    echo "[Somantic] Installing app....";
    cd app;
    npm install;
    cd ..;
fi

# install functions
if [ "$1" = "functions" ] 
then
    echo "[Somantic] Installing functions....";
    cd functions;
    python3.11 -m venv venv;              
    source venv/bin/activate;
    pip3 install --upgrade pip;
    python3.11 -m pip install -r requirements.txt;
    deactivate;
fi
