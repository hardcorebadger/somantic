# build and deploy the app
if [ "$1" = "app" ] 
then
  echo "[Somantic] Running develpment host for app...";
  cd app;
  npm run start;
fi

# deploy functions
if [ "$1" = "functions" ] 
then
  echo "[Somantic] Running emulators for functions...";
  firebase emulators:start --only functions;
fi