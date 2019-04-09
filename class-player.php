<?php
class player
{
	//Player's full name for display.  Uses first item in first_name array with last name and any trailing info- Jr, II, III etc
	public $full_name;
	
	//First name is an array because some places list a player differently, Jon/Jonathan, Ted/Teddy, Mike/Michael etc.  We're going to use the [0] key as the primary / most common first name if possible
	public $first_name = array();
	
	//Last name, without any suffix
	public $last_name;
	
	//Jr / II / III
	public $name_suffix;
	
	//Is this player starting today
	public $is_starting;
	
	//Does this player have a game scheduled today
	public $has_game;
	
	//Is this player injured
	public $is_injured;
	
	//Player's official status - Active / Minors / Suspended / 10D DL / etc
	public $roster_status;
	
	//Index is site name, value is all positions eligible on that site - ['yahoo'] = {'C', '2B'}
	public $eligible_pos = array();
	
	//If the player is starting, what is their position in the batting order
	public $order = '';
	
	//Array of IDs from various sites - ['bbrefID'] = 'Schwaky01', ['mlb'] = '656941', ['espn'] = '33712'
	public $player_id = array();
	
	//Player's main starting position
	public $pos;
	
	//Player bats L/R/S
	public $bats = '';
	
	//Player throws R/L
	public $throws = "";
	
	//Player's current team as object
	public $team;
	
	//Player's game data object - will be an array because of doubleheaders
	public $game;
	
	//Is the player playing at home today
	public $is_home;
	
	//Players stats for today's games
	public $daily_stats;
	
	
	public $batter_before = '';
	public $batter_after = '';
	public $status = '';
	public $opp_s_name = '';
	public $opp_s_id = '';
	public $opp_s_throws = '';
	public $opp_s_score = '';

	
	public $projection = 0;
	public $sum_pa = 0;
	public $sum_pts = 0;
	public $recent_average = 0;
	public $majors_average = 0;
	public $minors_average = 0;
	public $rnppa = 0;
	public $pa = 0;
	public $adj_projection = 0;
	public $sum_r_per_pa = '';
	public $splits = array();
	
	/*
	 *	Converts a player's name from latin encoded to standard English
	*/
	public function convert_name()
	{
		$latin_chars = array('Á' => "A", 'É' => "E", 'Í' => "I", 'Ó' => "O", 'Ú' => "U", 'á' => "a", 'é' => "e", 'í' => "i", 'ó' => "o", 'ú' => "u", 'Ñ' => "N", 'ñ' => "n", );
		$this->full_name = strtr($this->full_name, $latin_chars);
	}
	
	public function lookup_id()
	{
		$sql = "SELECT * FROM tbl_master WHERE yahoo_id  = " . $this->yahoo_id;
		$result = mysql_query($sql);
		if(mysql_num_rows($result) == 0)
		{
			$sql = "SELECT * FROM tbl_master WHERE full_name like '" . $this->full_name . "' AND status = 1";
			$result = mysql_query($sql);
			if(mysql_num_rows($result) == 0)
			{
				$rs=mysql_fetch_assoc($result);
				echo $sql . "<br>Couldn't find player " . $this->full_name . "<br/>";
				$sql = "INSERT INTO tbl_lost_players (name, team, pos) VALUES ('" . $this->full_name . "','" . $this->team . "','" . $this->pos . "')";
				mysql_query($sql);
			}
			if(mysql_num_rows($result) > 1)
			{
				echo $sql . "<br>Found too many players named " . $this->full_name . "<br/>";
				$sql = "INSERT INTO tbl_lost_players (name, team, pos) VALUES ('" . $this->full_name . "','" . $this->team . "','" . $this->pos . "')";
				mysql_query($sql);
			}
			if(mysql_num_rows($result) == 1)
			{
				$rs=mysql_fetch_assoc($result);
				$this->player_id = $rs['player_id'];
				$sql = "UPDATE tbl_master SET yahoo_id = " . $this->yahoo_id . " WHERE player_id = '" . $rs['player_id'] . "'";
				$result = mysql_query($sql);
			}
		}
		else
		{
			$rs=mysql_fetch_assoc($result);
			$this->player_id = $rs['player_id'];
		}
		if($this->player_id == '')
		{	
			//Couldn't lookup player_id
		}
	}

	
}
?>