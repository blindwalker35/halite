#!/bin/bash

if hash python3 2>/dev/null; then
	rm *.log
	rm *.hlt
    ./halite -d "30 30" "python3 BlindwalkerBot.py" "python3 1.0-BlindwalkerBot-RandomInternalMovement.py"
else
	rm *.log
	rm *.hlt
    ./halite -d "30 30" "python BlindwalkerBot.py" "python 1.0-BlindwalkerBot-RandomInternalMovement.py"
fi
