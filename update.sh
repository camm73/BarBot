#!/bin/bash

echo "Updating BarBot software..."
gitStatus=$(git pull)
if [ "$gitStatus" != "Already up to date." ]; then
	echo "Restarting BarBot to apply update"
	sleep 2
	sudo reboot
else
	echo "Nothing to update"
fi

exit 0
