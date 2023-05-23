## Some APIs

Base Url:

https://mk11-api.wbagora.com

| API                                                        | Description                                 |
| ---------------------------------------------------------- | ------------------------------------------- |
| /commerce/catalog/me/products                            | -                                           |
| /matches/current/me?page=1&fields=data&partial_response=1| Get match stats                             |
| /objects/season-definition/unique/<week_id>?fields=data&fields=server_data | Get Any Week at any time, needs api key only |
| /profiles/bulk/<profile_id>?partial_response=1           | My Profile, Can use it to get anyone's profile |
| /profiles/<profile_id>/inventory                         | Get All Items/skins                         |
| /ssc/invoke/daily_challenge_get                          | Shows you the reward if you do it           |
| /ssc/invoke/daily_challenge_reward                       | Daily challenge Get                         |
| /ssc/invoke/feed_get_unread                              | Notifications                               |
| /ssc/invoke/inventory_fetch_items                        | Get Items                                   |
| /ssc/invoke/inventory_fetch_loadouts                     | Get Edited Variations                       |
| /ssc/invoke/inventory_update                             | POST buy item                               |
| /ssc/invoke/match_completed                              | POST match complete                         |
| /ssc/invoke/portal_get_data                              | Requires X-NRS-VER and auth                  |
| /ssc/invoke/portal_get_persistent_event_data             | Offline Towers                              |
| /ssc/invoke/portal_season_get_current?season_slug=portal | Weekly Race                                 |
| /ssc/invoke/progression_get_krypt_data                   | -                                           |

Note: <profile_id> and <week_id> are placeholders for profile IDs and week IDs, respectively. Please replace them with the appropriate values when making requests.

You can use ASIMK11 as it taps into the API calls. Host your own forwarding server that will just send the requests back and forth between the game and wb's servers. mk11-mitm-server/server.py is a flask server that does just that, with example on how to modify the responses. In ASIMK11, point curl MITM to `http://localhost:12181`, and you will see all responses in the MITM. You can then proceed to save all requests's payloads and responses.
mk11-mitm-server/half_replicated_server.py was an attempt by me to replicate MK11's servers, but I got bored halfway through. Feel free to do what you want with it. Their servers accept JSON and will return JSON if MIME is `application/json` or anything else, and will return `x-ag` if it was `application/x-ag-binary`. Game only accepts `application/x-ag-binary` So make sure to convert the response back using `ag_conv` (which is incomplete).