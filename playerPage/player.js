
window.onSpotifyWebPlaybackSDKReady = () => {
	  const token = 'BQC7eGSJnsYHhl6HVX3wut6mPE7aFhDVkpr9LfnsjZQlGee5rP5HSeCFrk97NSoqilRgyPyZm_qY-7hDI4IYVb8qXPK3voDCU-BjZD8IZkiy89IxrxE6UMmuDF_o4pYZVAP3tjF-fvZPnq2dm2zF7DJfo6-MMzl6hIgYf9M';

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
