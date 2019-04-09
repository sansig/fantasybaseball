<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?php
/*
This is a little code snippet that runs every day and pulls the first MLB game start time and posts it to a google calendar I manage, which people can subscribe to and be notified.
*/
include('/home/zambartas/connection.php');
date_default_timezone_set('America/New_York');
require_once __DIR__ . '/google-api-php-client/src/Google/autoload.php';


define('APPLICATION_NAME', 'Google Calendar API PHP Quickstart');
define('CREDENTIALS_PATH', '~/.credentials/calendar-php-quickstart1.json');
define('CLIENT_SECRET_PATH', __DIR__ . '/client_secret.json');
define('SCOPES', implode(' ', array(
  Google_Service_Calendar::CALENDAR)
));

if (php_sapi_name() != 'cli') {
  throw new Exception('This application must be run on the command line.');
}

function getClient() {
  $client = new Google_Client();
  $client->setApplicationName(APPLICATION_NAME);
  $client->setScopes(SCOPES);
  $client->setAuthConfigFile(CLIENT_SECRET_PATH);
  $client->setAccessType('offline');

  // Load previously authorized credentials from a file.
  $credentialsPath = expandHomeDirectory(CREDENTIALS_PATH);
  if (file_exists($credentialsPath)) {
    $accessToken = file_get_contents($credentialsPath);
  } else {
    // Request authorization from the user.
    $authUrl = $client->createAuthUrl();
    printf("Open the following link in your browser:\n%s\n", $authUrl);
    print 'Enter verification code: ';
    $authCode = trim(fgets(STDIN));

    // Exchange authorization code for an access token.
    $accessToken = $client->authenticate($authCode);

    // Store the credentials to disk.
    if(!file_exists(dirname($credentialsPath))) {
      mkdir(dirname($credentialsPath), 0700, true);
    }
    file_put_contents($credentialsPath, $accessToken);
    printf("Credentials saved to %s\n", $credentialsPath);
  }
  $client->setAccessToken($accessToken);

  // Refresh the token if it's expired.
  if ($client->isAccessTokenExpired()) {
    $client->refreshToken($client->getRefreshToken());
    file_put_contents($credentialsPath, $client->getAccessToken());
  }
  return $client;
}

$sql = "SELECT min(gt) as t, FROM_UNIXTIME( min(gt),'%h:%i %p') as first_game FROM `tbl_mlb_game_data` WHERE `game_date` = CURDATE()";
$results1 = mysql_query($sql);
$rs1=mysql_fetch_assoc($results1);
$game_time = date('h:ia', $rs1['t']);
$unix_time = date('Y-m-d\TH:i:s', $rs1['t']);
$client = getClient();
$service = new Google_Service_Calendar($client);
$event = new Google_Service_Calendar_Event(array(
  'summary' => 'First Pitch',
  'description' => 'Details about today\'s game',
  'start' => array(
    'dateTime' => $unix_time,
    'timeZone' => 'America/New_York',
  ),
  'end' => array(
    'dateTime' => $unix_time,
    'timeZone' => 'America/New_York',
  ),
));
$calendarId = 'cmgltbndnbrhvdhpg5m6qn4qpk@group.calendar.google.com';
$event = $service->events->insert($calendarId, $event);
printf('Event created: %s\n', $event->htmlLink);