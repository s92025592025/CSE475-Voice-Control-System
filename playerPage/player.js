"use strict"

window.onSpotifyWebPlaybackSDKReady = () => {
	  const token = 'BQAPXFvmhuM0Akpct6cpzY6JC2-2BJvHKNB58fVjSHoPlEKlL3qjXExZxKJmwdNci185I2kK7ZNfnqSY74QSmWbsRFtEzag2OVoxMByb_GPIFdgPPKk3ERNbFx54UIqm5Y_Ee6dQJbw6A-kQXHTNsctyvl7DZ-_rAF9rk3mrNcjs5WZOG66lQnzIkhxa';

	  const player = new Spotify.Player({
		  name: 'Web Playback SDK Quick Start Player',
		  getOAuthToken: cb => { cb(token); }
	  });

	  // Error handling
	  player.addListener('initialization_error', ({ message }) => { console.error(message); });
	  player.addListener('authentication_error', ({ message }) => { console.error(message); });
	  player.addListener('account_error', ({ message }) => { console.error(message); });
	  player.addListener('playback_error', ({ message }) => { console.error(message); });

	  // Playback status updates
	  player.addListener('player_state_changed', state => { console.log(state); });

	  // Ready
	  player.addListener('ready', ({ device_id }) => {
		  console.log('Ready with Device ID', device_id);
	  });

	  // Not Ready
	  player.addListener('not_ready', ({ device_id }) => {
		  console.log('Device ID has gone offline', device_id);
	  });

	  // Connect to the player!
	  player.connect();
};
