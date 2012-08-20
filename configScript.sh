# Move or delete files from selected user
if [[ $move_yes_no == 1 ]]; then
	# move
	mkdir -p /Users/{$user}/Documents/Student\ Files/
	mv /Users/{$user}/Desktop/* /Users/{$user}/Documents/Student\ Files/
else
	# delete
	rm -rf /Users/{$user}/Desktop/*
fi

# Set homepage for Firefox and Safari
# Firefox
sed -i 's|\("browser.startup.homepage",\) "\(.*\)"|\1 "${homepage}"|' /Users/{$user}/Library/Application Support/Firefox/*.default/prefs.js
# Safari
defaults write com.apple.Safari HomePage "{$homepage}"
defaults write com.apple.internetconfigpriv WWWHomePage "{$homepage}"

# Power Management Settings
# Battery
pmset -b sleep 10 displaysleep 5
# Charger
pmset -c sleep 30 displaysleep 0
# UPS
pmset -b sleep 10 displaysleep 5
# Set startup time
sudo pmset repeat wakeorpoweron MTWRF $startup
# Set shutdown time
sudo pmset repeat shutdown MTWRFSU $shutdown