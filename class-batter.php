<?php
class batter extends player
{
	//Array for actual stats indexed by game{0,1} in case of a doubleheader i.e. $batter->stats[0]['H'] = batters hits recorded in the first game of the day.  $batter->stats[1]['H'] = Hits in the second game, if neccesary
	public $stats = array();
	
	//Array for various batter split data i.e. vs RHP/LHP
	public $splits = array();

	/*
		Find out if the batter has a game, and is starting
		@vars $is_starting bool
		@vars $order {1-9}
		@vars $game object
	*/
	public function check_game_status()
	{
		
	}
	
	/*
		Update the database with live stats
	*/
	public function update_stats_in_db()
	{
		
	}
	
	/*
		Pull latest split data from db
	*/
	public function load_db_splits()
	{
		$current_year = date("Y");
		$sum_recent_pa = 0;
		
		//Find all splits related to the batter's current game situation
		$sql = "SELECT * FROM tbl_batter_splits WHERE player_id = '" . $this->player_id . "' and season = " . $current_year;
		$results=mysql_query($sql);
		while($rs=mysql_fetch_assoc($results))
		{
			//Update each individual split but keep a running tally to average at the end
			if($rs['split_type'] == $this->splits['tod']['value'])
			{
				$this->splits_pts += $rs['pts'];
				$this->splits_pa += $rs['PA'];
				$this->splits['tod']['pts'] = $rs['pts'];
				$this->splits['tod']['pa'] = $rs['PA'];
				if($rs['PA'] > 0)
					$this->splits['tod']['pts_per_pa'] = number_format($rs['pts']/$rs['PA'],2);
			}
			if($rs['split_type'] == $this->splits['home']['value'])
			{
				$this->splits_pts += $rs['pts'];
				$this->splits_pa += $rs['PA'];
				$this->splits['home']['pts'] = $rs['pts'];
				$this->splits['home']['pa'] = $rs['PA'];
				if($rs['PA'] > 0)
					$this->splits['home']['pts_per_pa'] = number_format($rs['pts']/$rs['PA'],2);
			}
			if($rs['split_type'] == $this->splits['opp']['value'])
			{
				$this->splits_pts += $rs['pts'];
				$this->splits_pa += $rs['PA'];
				$this->splits['opp']['pts'] = $rs['pts'];
				$this->splits['opp']['pa'] = $rs['PA'];
				if($rs['PA'] > 0)
					$this->splits['opp']['pts_per_pa'] = number_format($rs['pts']/$rs['PA'],2);
			}
			if($rs['split_type'] == $this->splits['opp_s_id']['value'])
			{
				$this->splits_pts += $rs['pts'];
				$this->splits_pa += $rs['PA'];
				$this->splits['opp_s_id']['pts'] = $rs['pts'] + (($this->sum_r_per_pa * $rs['PA'])*6);
				$this->splits['opp_s_id']['pa'] = $rs['PA'];
				$this->splits['opp_s_id']['ops'] = $rs['OPS'];
				if($rs['PA'] > 0)
					$this->splits['opp_s_id']['pts_per_pa'] = number_format($this->splits['opp_s_id']['pts']/$this->splits['opp_s_id']['pa'],2);
			}
		}
		
		//If we have any split data, let's get the average of it all
		$this->projection = $this->splits_pa > 0 ? number_format($this->splits_pts / $this->splits_pa,2) : 0;
		
		//Skew the number based on recent performanace
		$adj_factor = ($this->majors_average > 0 && $this->recent_average > 0) ? $this->recent_average/$this->majors_average : 0;
		$this->adj_projection = number_format($this->projection * $adj_factor,2);
		
		$this->projection_ratio = number_format((($this->adj_projection / $this->recent_average)-1)*100,0);
	}
	
	/*
		Update the db with the latest projection for this batter
	*/
	public function update_db_predictions()
	{
		$sql = "INSERT INTO `tbl_predictions_batters` (`player_id`, `full_name`, `game_date`, `opp_team`, `opp_s_id`, `opp_s_name`, `opp_s_throws`, `opp_s_score`, `loc`, `site`, `tod`, `pos`, `order`, `batter_before`, `batter_after`, `combined_pa`, `projection`, `percent_change`, `opp_scores`, `tod_score`, `home_away_score`, `opp_s_id_score`, `opp_s_id_ops`, `opp_s_id_pa`, `pitch_type_score`) VALUES ('" . $this->player_id . "', '" . $this->full_name . "', '" . $this->game->game_date . "', '" . $this->opp_t . "','" . $this->opp_s_id . "', '" . $this->opp_s_name . "', '" . $this->opp_s_throws . "', '" . $this->opp_s_score . "', '" . $this->splits['home']['value'] . "', '" . $this->opp_t . "', '" . $this->splits['tod']['value'] . "', '" . $this->pos . "', '" . $this->order . "', '" . $this->batter_before . "', '" . $this->batter_after . "', '" . $this->splits_pa . "', '" . $this->projection . "', '" . $this->projection_ratio . "', '" . $this->splits['opp']['pts_per_pa'] . "', '" . $this->splits['tod']['pts_per_pa'] . "', '" . $this->splits['home']['pts_per_pa'] . "', '" . $this->splits['opp_s_id']['pts_per_pa'] . "', '" . $this->splits['opp_s_id']['ops'] . "', '" . $this->splits['opp_s_id']['pa'] . "', '" . $this->splits['pitch_type_score'] . "')";
		mysql_query($sql);
	}
	
	/*
		TODO: This belongs in the game class
	*/
	public function adj_game_time_zone()
	{
		$start_time = explode(" ", $this->start_time);
		$am_pm = $start_time[1];
		$start_time = explode(":", $start_time[0]);
		$player->start_time_local = $start_time[0];	
		if($am_pm == "PM" && $player->start_time_local <> "12")
			$player->start_time_local = $player->start_time_local+12;		
	}
	
	/*
		Raw output of split data
	*/
	public function show_splits()
	{
		foreach($this->splits as $key => $value)
		{
			echo $key . " " . $value . "<br>";
		}
	}

	/*
		Load all available projections for this batter for each game scheduled
	*/
	public function load_db_projections()
	{
		
	}
	
	
	
}
?>