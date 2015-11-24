# Raspi LED Controller client thingy.

This runs on a raspberry pi model b in the cupboard in the workflow room in Toronto. It controls the LED strips connected to it. 

It listens to an HTTP SSE stream from the wf-lights app running on heroku. 

It's very rudimentary, is deployed via git checkout, and runs inside of supervisord.
If it stops responding, you can kick it via supervisor.
```
  ssh pi@workflowypi.local
  sudo supervisorctl stop lightsclient
  sudo supervisorctl start lightsclient
```

If you need to deploy a new version, just pull the master branch:
```
   ssh pi@workflowypi.local
   sudo -i
   cd /home/jason/wf-lights-client
   git pull
```

