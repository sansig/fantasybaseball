<?php
session_start();
$page_title = "Daily Predictions";
include('/home/micsan58/sansig.com/mlb/includes/connection.php');
include('/home/micsan58/sansig.com/mlb/includes/header.php');
?>
<body>

<table class="teamtable">
<?php
set_time_limit(0);
$sql = "SELECT MIN(`gt`) as min_gt, MAX(`gt`) as max_gt FROM tbl_mlb_game_data a WHERE a.`game_date` = CURDATE()";

$results = mysql_query($sql);
//e($sql);
$rs=mysql_fetch_assoc($results);

$url = "";
$year = date('Y');
$team = $_GET['t'];
$filter = $_GET['filter'];
if($_GET['filter'] == 'filter1')
	$filter1 = true;
if($_GET['filter'] == 'filter2')
	$filter2 = true;
if($_GET['filter'] == 'filter3')
	$filter3 = true;
$gt_start = $_GET['gt_start'];
$gt_end = $_GET['gt_end'];
if($_GET['gt_start'] <> '')
{
	$gt_start = $_GET['gt_start'];
}
else
{
	$gt_start = $rs['min_gt'];
}
if($_GET['gt_end'] <> '')
{
	$gt_end = $_GET['gt_end'];
}
else
{
	$gt_end = $rs['max_gt'];
}
if($_GET['pos'] <> '')
{
	$pos = $_GET['pos'];
}
else
{
	$pos = 'All';
}

$pos_sql = " AND b.pos = '" . $pos . "' ";
if($pos == 'All')
	$pos_sql = '';
echo "<table id=\"game_list\">";
$sql = "SELECT *, a.location as game_location FROM tbl_mlb_game_data a, v_team_avg_performance b, v_pitcher_team_stats c WHERE a.team_name = b.team_name AND a.team_name = c.team_name AND c.starting = 0 AND a.season = c.season AND a.season = b.season AND a.`game_date` = CURDATE() AND a.location = 'home' ORDER BY a.game_date, a.gt, a.site asc, a.location DESC";
$sql = "SELECT *, a.location as game_location FROM tbl_mlb_game_data a WHERE a.`game_date` = CURDATE() AND a.location = 'home' ORDER BY a.game_date, a.gt, a.site asc, a.location DESC";

$results = mysql_query($sql);
//e($sql);
echo "<tr><form id=\"dfs\" name=\"dfs\" action=\"\" method=\"get\">";
while($rs=mysql_fetch_assoc($results))
{
	$checked = '';
	if($gt_start == $rs['gt'])
		$checked = ' checked="checked"';
	echo "<td>" . $rs['opp_abv'] . "<br>" . $rs['team_abv'] . " " . $rs['game_time'] . "<input type=\"radio\" name=\"gt_start\" value=\"" . $rs['gt'] . "\" style=\"display:inline\"" . $checked . " onchange=\"javascript:update_dfs();\"></td>";
}
echo "</tr><tr>";
mysql_data_seek($results, 0);
while($rs=mysql_fetch_assoc($results))
{
	$checked = '';
	if($gt_end == $rs['gt'])
		$checked = ' checked="checked"';
	echo "<td>" . $rs['opp_abv'] . "<br>" . $rs['team_abv'] . " " . $rs['game_time'] . "<input type=\"radio\" name=\"gt_end\" value=\"" . $rs['gt'] . "\" style=\"display:inline\"" . $checked . " onchange=\"javascript:update_dfs();\"></td>";
}
echo "</tr><tr>";
$sql = "SELECT position_text from tbl_positions WHERE league_id = 0 ORDER BY sort_order ASC";
$results = mysql_query($sql);
while($rs=mysql_fetch_assoc($results))
{
	$checked = '';
	if($pos == $rs['position_text'])
		$checked = ' checked="checked"';
	echo "<td><input type=\"radio\" name=\"pos\" value=\"" . $rs['position_text'] . "\"" . $checked . " onchange=\"javascript:update_dfs();\">" . $rs['position_text'] . "</td>";
}

echo "<tr><td><input type=\"hidden\" value=\"" . $_GET['sort']  . "\" name=\"sort\"></td>";
echo "<tr><td><input type=\"radio\" value=\"\" name=\"filter\">No filter</td>";
$checked = '';
if($filter == 'filter1')
	$checked = ' checked="checked"';
echo "<td><input type=\"radio\" value=\"filter1\" name=\"filter\"" . $checked  . ">Filter1</td>";
$checked = '';
if($filter == 'filter2')
	$checked = ' checked="checked"';
echo "<td><input type=\"radio\" value=\"filter2\" name=\"filter\"" . $checked  . ">Filter2</td>";
$checked = '';
if($filter == 'filter3')
	$checked = ' checked="checked"';
echo "<td><input type=\"radio\" value=\"filter3\" name=\"filter\"" . $checked  . ">Filter3</td>";
$checked = '';
if($filter == 'hr_filter')
	$checked = ' checked="checked"';
echo "<td><input type=\"radio\" value=\"hr_filter\" name=\"filter\"" . $checked  . ">HR Filter</td>";
$checked = '';
echo "<td><input type=\"submit\" value=\"update\"></form></td></tr>";
if($_GET['sort'] <> '')
{
	switch($_GET['sort'])
	{
		case 'overall':
			$sort = 'fd_avg_pts  DESC';
			break;
		case 'overall_value':
			$sort = 'overall_value  DESC';
			break;
		default:
			$sort = 'fd_avg_pts  DESC';	
	}
}
else
{
	$sort = 'fd_avg_pts  DESC';
}

if($pos <> 'P')
{
	$sql = "SELECT a.player_id, a.player_name, a.player_bats, a.`pos`,
	a.team,a.opp_team, a.game_date, 
	a.gt, a.estimated, 
	round(avg(a.park_adjusted_ops),3) AS  `OPS_lineup` ,
	a.platoon_pa as batter_ab,
	a.opp_s_id as starter, a.opp_s_throws, 
	a.batting_order,
	a.adi,
	a.wind_speed,
	a.wind_direction,
	a.loc,
	a.pop,
	a.fd_salary,
	b.pos as fd_pos,
	a.`vs. Power`,
	a.`vs. avg.P/F`,
	a.`vs. Finesse`,
	a.`vs. Fly Ball`,
	a.`vs. avg.F/G`,
	a.`vs. GrndBall`,
	a.sb_rate,
	a.k_rate,
	a.hr_rate,
	a.opp_sp_sb_rate,
	a.opp_sp_k_rate,
	a.opp_sp_hr_rate,
	b.fd_salary as salary,
	b.nf_pts,
	b.nf_value,
	b.rg_pts,
	b.rg_value,
	round((a.opp_sp_ops),3) AS `OPS_opposing_pitcher`,
	round(overall_park_adjusted_ops,3) as overall_OPS,
	(((opp_sp_ops+overall_park_adjusted_ops+opp_sp_power_type+opp_sp_gb_fb_type))-.8)*4 as fd_pts_fix,
	(((opp_sp_ops+overall_park_adjusted_ops)*2)-.8)*4 as fd_pts ,
	(b.nf_pts + b.rg_pts + (((overall_park_adjusted_ops*4)-.8)*4))/3 as fd_avg_pts,
	((b.nf_pts + b.rg_pts + (((overall_park_adjusted_ops*4)-.8)*4))/3)/(b.fd_salary/1000) as overall_value
	FROM  `tbl_lineups` a, tbl_player_stats b WHERE 
	a.player_name = replace(b.full_name, '-',' ')
	AND a.pos <> 'P'
	AND gt >= " . $gt_start . "
	AND gt <= " . $gt_end . $pos_sql . " AND b.game_date = CURDATE() GROUP BY a.team_name, a.player_id
	ORDER BY " . $sort;
	e($sql);
	$results = mysql_query($sql);
	if(mysql_num_rows($results) > 0)
	{
		echo "<table>";
			//echo "<tr><td>Player id</td>";
			echo "<td>Name</td>";
			echo "<td>NF Pts</td>";
			echo "<td>RG Pts</td>";
			echo "<td>MS Pts</td>";
			echo "<td><a href=\"./daily_fantasy_baseball.php?sort=overall&amp;gt_start=" . $gt_start . "&amp;gt_end=" . $gt_end . "\">Overall</a></td>";
			echo "<td>NF Val</td>";
			echo "<td>RG Val</td>";
			echo "<td>MS Val</td>";
			echo "<td><a href=\"./daily_fantasy_baseball.php?sort=overall_value&amp;gt_start=" . $gt_start . "&amp;gt_end=" . $gt_end . "\">Overall Val</a></td>";
			echo "<td>OPS</td>";
			echo "<td>AB</td>";
			echo "<td>Bats</td>";
			//echo "<td>Throws</td>";
			echo "<td>Order</td>";
			echo "<td>Team</td>";
			echo "<td>Opp</td>";
			echo "<td>Pos</td>";
			echo "<td>Salary</td>";
			echo "<td>Location</td>";
			echo "<td>OPS Split</td>";
			echo "<td>Opp Starter</td>";
			echo "<td>Starter OPS</td>";
			echo "<td>Pwr Split</td>";
			echo "<td>GB Split</td>";
			echo "<td>SB rate B</td>";
			echo "<td>SB rate P</td>";
			echo "<td>K rate B</td>";
			echo "<td>K rate P</td>";
			echo "<td>HR rate B</td>";
			echo "<td>HR rate P</td>";
			echo "<td>ADI</td>";
			echo "<td>Wind Dir</td>";
			echo "<td>Wind spd</td>";
			echo "<td>POP</td>";
			echo "</tr>";
		while($rs=mysql_fetch_assoc($results))
		{
			/*
			$sql = "SELECT 
			c.bb_per_bf,
			c.k_per_bf,
			c.gb_fb_ratio
			FROM  v_pitcher_stats c WHERE c.player_id = '" . $rs['starter'] . "' AND c.season = 2015 AND c.`starting` = 1";
			//e($sql);
			$results_sp = mysql_query($sql);
			$rs_sp = mysql_fetch_assoc($results_sp);
			//ed($rs_sp['k_per_bf']);
			if($rs_sp['k_per_bf'] + $rs_sp['bb_per_bf'] > .28)
			{
				$power_split = $rs['vs. Power'];
			}
			elseif($rs_sp['k_per_bf'] + $rs_sp['bb_per_bf'] < .23)
			{
				$power_split = $rs['vs. Finesse'];
			}
			else
			{
				$power_split = $rs['vs. avg.P/F'];	//.26 is average in 2015
			}
			
			if(($rs_sp['gb_fb_ratio']) > 1.03)
			{
				$gb_split = $rs['vs. Fly Ball'];
			}
			elseif(($rs_sp['gb_fb_ratio'])< .75)	//.89 is average in 2015
			{
				$gb_split = $rs['vs. GrndBall'];
			}
			else
			{
				$gb_split = $rs['vs. avg.F/G'];
			}
			$average_ops = (($power_split + $gb_split + $rs['OPS_opposing_pitcher'] + $rs['OPS_lineup'])/4);
			*/
			$average_ops = (($rs['OPS_opposing_pitcher'] + $rs['OPS_lineup'])/2);
			$fd_pts = (($rs['overall_OPS'] * 4)-.8)*4;
			if($rs['opp_s_throws'] == $rs['player_bats'])
			{
				$handedness = 'low';
			}
			else
			{
				$handedness = 'high';
			}
			
			/*
			if($filter1 == true)
			{
				if($power_split > .71 && $gb_split > .71 && $rs['OPS_opposing_pitcher'] > .71 && $rs['fd_pts'] > 2.5 && $rs['OPS_lineup'] > .71)
				{
					$teams[$rs['team']]++;
					echo "<tr>";
					echo "<td><a href=\"https://www.sansig.com/mlb/dfs_show_player.php?player_id=" . $rs['player_id'] . "\" target=\"new\">" . $rs['player_id'] . "</a></td>";
					echo "<td class=\"" . check_sub_rate(($rs['estimated']), 1) . "\">" . $rs['player_name'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['fd_pts']), 2.5, 1.5) . "\">" . round($rs['fd_pts'],1) . "</td>";
					echo "<td class=\"" . check_multi_rate(($fd_pts), 3.0, 2.0) . "\">" . round($fd_pts,1) . "</td>";
					echo "<td class=\"" . check_rate(($average_ops), .710) . "\">" . number_format($average_ops,3) . "</td>";
					echo "<td class=\"" . check_rate(($rs['batter_ab']), 100) . "\">" . $rs['batter_ab'] . "</td>";
					echo "<td>" . $rs['player_bats'] . "</td>";
					echo "<td>" . $rs['opp_s_throws'] . "</td>";
					echo "<td>" . $rs['batting_order'] . "</td>";
					echo "<td>" . $rs['team'] . "</td>";
					echo "<td>" . $rs['opp_team'] . "</td>";
					echo "<td>" . $rs['fd_pos'] . "</td>";
					echo "<td>" . number_format($rs['fd_salary']/1000,1) . "</td>";
					echo "<td>" . $rs['loc'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_lineup']), .710) . "\">" . $rs['OPS_lineup'] . "</td>";
					echo "<td>" . $rs['starter'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_opposing_pitcher']), .710) . "\">" . $rs['OPS_opposing_pitcher'] . "</td>";
					//echo "<td>" . $rs_sp['k_per_bf'] . "</td>";
					//echo "<td>" . $rs_sp['bb_per_bf'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($power_split),.8, .6) . "\">" . $power_split . "</td>";
					echo "<td class=\"" . check_multi_rate(($gb_split), .8, .6) . "\">" . $gb_split . "</td>";
					//echo "<td>" . $rs['gb_fb_ratio'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['sb_rate']), .025, 0) . "\">" . $rs['sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_sb_rate']), .015, 0) . "\">" . $rs['opp_sp_sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['k_rate']),.25, .15) . "\">" . $rs['k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_k_rate']), .15, .25) . "\">" . $rs['opp_sp_k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['hr_rate']), .045 , .028) . "\">" . $rs['hr_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_hr_rate']), .045, .028) . "\">" . $rs['opp_sp_hr_rate'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['adi']), 61) . "\">" . $rs['adi'] . "</td>";
					echo "<td class=\"" . $wind_direction . "\">" . $rs['wind_direction'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['wind_speed']), 8) . "\">" . $rs['wind_speed'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['pop']), 25) . "\">" . $rs['pop'] . "%</td>";
					echo "</tr>";
				}
			}
			elseif($filter2 == true)
			{
				$score = 0;
				if($power_split > .71)
					$score++;
				if($gb_split > .71)
					$score++;
				if($rs['OPS_opposing_pitcher'] > .71)
					$score++;
				if($rs['OPS_lineup'] > .71)
					$score++;
				if($rs['fd_pts'] > 2.5)
					$score++;
				if($score >= 3)
				{
					$teams[$rs['team']]++;
					echo "<tr>";
					echo "<tr>";
					echo "<td><a href=\"https://www.sansig.com/mlb/dfs_show_player.php?player_id=" . $rs['player_id'] . "\" target=\"new\">" . $rs['player_id'] . "</a></td>";
					echo "<td class=\"" . check_sub_rate(($rs['estimated']), 1) . "\">" . $rs['player_name'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['fd_pts']), 2.5, 1.5) . "\">" . round($rs['fd_pts'],1) . "</td>";
					echo "<td class=\"" . check_multi_rate(($fd_pts), 3.0, 2.0) . "\">" . round($fd_pts,1) . "</td>";
					echo "<td class=\"" . check_rate(($average_ops), .710) . "\">" . number_format($average_ops,3) . "</td>";
					echo "<td class=\"" . check_rate(($rs['batter_ab']), 100) . "\">" . $rs['batter_ab'] . "</td>";
					echo "<td>" . $rs['player_bats'] . "</td>";
					echo "<td>" . $rs['opp_s_throws'] . "</td>";
					echo "<td>" . $rs['batting_order'] . "</td>";
					echo "<td>" . $rs['team'] . "</td>";
					echo "<td>" . $rs['opp_team'] . "</td>";
					echo "<td>" . $rs['fd_pos'] . "</td>";
					echo "<td>" . number_format($rs['fd_salary']/1000,1) . "</td>";
					echo "<td>" . $rs['loc'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_lineup']), .710) . "\">" . $rs['OPS_lineup'] . "</td>";
					echo "<td>" . $rs['starter'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_opposing_pitcher']), .710) . "\">" . $rs['OPS_opposing_pitcher'] . "</td>";
					//echo "<td>" . $rs_sp['k_per_bf'] . "</td>";
					//echo "<td>" . $rs_sp['bb_per_bf'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($power_split),.8, .6) . "\">" . $power_split . "</td>";
					echo "<td class=\"" . check_multi_rate(($gb_split), .8, .6) . "\">" . $gb_split . "</td>";
					//echo "<td>" . $rs['gb_fb_ratio'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['sb_rate']), .025, 0) . "\">" . $rs['sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_sb_rate']), .015, 0) . "\">" . $rs['opp_sp_sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['k_rate']),.25, .15) . "\">" . $rs['k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_k_rate']), .15, .25) . "\">" . $rs['opp_sp_k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['hr_rate']), .045 , .028) . "\">" . $rs['hr_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_hr_rate']), .045, .028) . "\">" . $rs['opp_sp_hr_rate'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['adi']), 61) . "\">" . $rs['adi'] . "</td>";
					echo "<td class=\"" . $wind_direction . "\">" . $rs['wind_direction'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['wind_speed']), 8) . "\">" . $rs['wind_speed'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['pop']), 25) . "\">" . $rs['pop'] . "%</td>";
					echo "</tr>";
				}
			}
			elseif($filter3 == true)
			{
				$score = 0;
				if(((($power_split + $gb_split + $rs['OPS_opposing_pitcher'] + $rs['OPS_lineup'])/4) > .71) && $rs['fd_pts'] > 2.5)
				{
					$teams[$rs['team']]++;
					echo "<tr>";
					echo "<tr>";
					echo "<td><a href=\"https://www.sansig.com/mlb/dfs_show_player.php?player_id=" . $rs['player_id'] . "\" target=\"new\">" . $rs['player_id'] . "</a></td>";
					echo "<td class=\"" . check_sub_rate(($rs['estimated']), 1) . "\">" . $rs['player_name'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['fd_pts']), 2.5, 1.5) . "\">" . round($rs['fd_pts'],1) . "</td>";
					echo "<td class=\"" . check_multi_rate(($fd_pts), 3.0, 2.0) . "\">" . round($fd_pts,1) . "</td>";
					echo "<td class=\"" . check_rate(($average_ops), .710) . "\">" . number_format($average_ops,3) . "</td>";
					echo "<td class=\"" . check_rate(($rs['batter_ab']), 100) . "\">" . $rs['batter_ab'] . "</td>";
					echo "<td>" . $rs['player_bats'] . "</td>";
					echo "<td>" . $rs['opp_s_throws'] . "</td>";
					echo "<td>" . $rs['batting_order'] . "</td>";
					echo "<td>" . $rs['team'] . "</td>";
					echo "<td>" . $rs['opp_team'] . "</td>";
					echo "<td>" . $rs['fd_pos'] . "</td>";
					echo "<td>" . number_format($rs['fd_salary']/1000,1) . "</td>";
					echo "<td>" . $rs['loc'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_lineup']), .710) . "\">" . $rs['OPS_lineup'] . "</td>";
					echo "<td>" . $rs['starter'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_opposing_pitcher']), .710) . "\">" . $rs['OPS_opposing_pitcher'] . "</td>";
					//echo "<td>" . $rs_sp['k_per_bf'] . "</td>";
					//echo "<td>" . $rs_sp['bb_per_bf'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($power_split),.8, .6) . "\">" . $power_split . "</td>";
					echo "<td class=\"" . check_multi_rate(($gb_split), .8, .6) . "\">" . $gb_split . "</td>";
					//echo "<td>" . $rs['gb_fb_ratio'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['sb_rate']), .025, 0) . "\">" . $rs['sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_sb_rate']), .015, 0) . "\">" . $rs['opp_sp_sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['k_rate']),.25, .15) . "\">" . $rs['k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_k_rate']), .15, .25) . "\">" . $rs['opp_sp_k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['hr_rate']), .045 , .028) . "\">" . $rs['hr_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_hr_rate']), .045, .028) . "\">" . $rs['opp_sp_hr_rate'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['adi']), 61) . "\">" . $rs['adi'] . "</td>";
					echo "<td class=\"" . $wind_direction . "\">" . $rs['wind_direction'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['wind_speed']), 8) . "\">" . $rs['wind_speed'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['pop']), 25) . "\">" . $rs['pop'] . "%</td>";
					echo "</tr>";
				}
			}
			elseif($filter == 'hr_filter')
			{
				$score = 0;
				if($rs['hr_rate'] > .04 && $rs['opp_sp_hr_rate'] > .025)
				{
					$teams[$rs['team']]++;
					echo "<tr>";
					echo "<tr>";
					echo "<td><a href=\"https://www.sansig.com/mlb/dfs_show_player.php?player_id=" . $rs['player_id'] . "\" target=\"new\">" . $rs['player_id'] . "</a></td>";
					echo "<td class=\"" . check_sub_rate(($rs['estimated']), 1) . "\">" . $rs['player_name'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['fd_pts']), 2.5, 1.5) . "\">" . round($rs['fd_pts'],1) . "</td>";
					echo "<td class=\"" . check_multi_rate(($fd_pts), 3.0, 2.0) . "\">" . round($fd_pts,1) . "</td>";
					echo "<td class=\"" . check_rate(($average_ops), .710) . "\">" . number_format($average_ops,3) . "</td>";
					echo "<td class=\"" . check_rate(($rs['batter_ab']), 100) . "\">" . $rs['batter_ab'] . "</td>";
					echo "<td>" . $rs['player_bats'] . "</td>";
					echo "<td>" . $rs['opp_s_throws'] . "</td>";
					echo "<td>" . $rs['batting_order'] . "</td>";
					echo "<td>" . $rs['team'] . "</td>";
					echo "<td>" . $rs['opp_team'] . "</td>";
					echo "<td>" . $rs['fd_pos'] . "</td>";
					echo "<td>" . number_format($rs['fd_salary']/1000,1) . "</td>";
					echo "<td>" . $rs['loc'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_lineup']), .710) . "\">" . $rs['OPS_lineup'] . "</td>";
					echo "<td>" . $rs['starter'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_opposing_pitcher']), .710) . "\">" . $rs['OPS_opposing_pitcher'] . "</td>";
					//echo "<td>" . $rs_sp['k_per_bf'] . "</td>";
					//echo "<td>" . $rs_sp['bb_per_bf'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($power_split),.8, .6) . "\">" . $power_split . "</td>";
					echo "<td class=\"" . check_multi_rate(($gb_split), .8, .6) . "\">" . $gb_split . "</td>";
					//echo "<td>" . $rs['gb_fb_ratio'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['sb_rate']), .025, 0) . "\">" . $rs['sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_sb_rate']), .015, 0) . "\">" . $rs['opp_sp_sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['k_rate']),.25, .15) . "\">" . $rs['k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_k_rate']), .15, .25) . "\">" . $rs['opp_sp_k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['hr_rate']), .06 , .04) . "\">" . $rs['hr_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_hr_rate']), .045, .028) . "\">" . $rs['opp_sp_hr_rate'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['adi']), 61) . "\">" . $rs['adi'] . "</td>";
					echo "<td class=\"" . $wind_direction . "\">" . $rs['wind_direction'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['wind_speed']), 8) . "\">" . $rs['wind_speed'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['pop']), 25) . "\">" . $rs['pop'] . "%</td>";
					echo "</tr>";
				}
			}
			else
			*/
			{
					echo "<tr>";
					//echo "<td><a href=\"https://www.sansig.com/mlb/dfs_show_player.php?player_id=" . $rs['player_id'] . "\" target=\"new\">" . $rs['player_id'] . "</a></td>";
					echo "<td class=\"" . check_sub_rate(($rs['estimated']), 1) . "\">" . $rs['player_name'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['nf_pts']), 9.0, 7.0) . "\">" . $rs['nf_pts'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['rg_pts']), 9.0, 7.0) . "\">" . $rs['rg_pts'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['fd_pts']), 9.0, 7.0) . "\">" . round($fd_pts,2) . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['fd_avg_pts']), 9,6) . "\">" . number_format($rs['fd_avg_pts'],2) . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['nf_value']), 3.75, 3.2) . "\">" . $rs['nf_value'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['rg_value']), 3, 2.5) . "\">" . $rs['rg_value'] . "</td>";
					if($rs['salary'] <> 0)
						$fd_pts = ($fd_pts/($rs['salary']/1000));
					echo "<td class=\"" . check_multi_rate(($fd_pts), 3.75,3) . "\">" . number_format($fd_pts,2) . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['overall_value']), 3, 2.5) . "\">" . number_format($rs['overall_value'],2) . "</td>";
					echo "<td class=\"" . check_multi_rate(($average_ops), .750, .700) . "\">" . number_format($average_ops,3) . "</td>";
					echo "<td class=\"" . check_rate(($rs['batter_ab']), 100) . "\">" . $rs['batter_ab'] . "</td>";
					echo "<td class=\"" . $handedness . "\">" . $rs['player_bats'] . "</td>";
					//echo "<td>" . $rs['opp_s_throws'] . "</td>";
					echo "<td>" . $rs['batting_order'] . "</td>";
					echo "<td>" . $rs['team'] . "</td>";
					echo "<td>" . $rs['opp_team'] . "</td>";
					echo "<td>" . $rs['fd_pos'] . "</td>";
					echo "<td>" . number_format($rs['salary']/1000,1) . "</td>";
					echo "<td>" . $rs['loc'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_lineup']), .710) . "\">" . $rs['OPS_lineup'] . "</td>";
					echo "<td>" . $rs['starter'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['OPS_opposing_pitcher']), .710) . "\">" . $rs['OPS_opposing_pitcher'] . "</td>";
					//echo "<td>" . $rs_sp['k_per_bf'] . "</td>";
					//echo "<td>" . $rs_sp['bb_per_bf'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($power_split),.8, .6) . "\">" . $power_split . "</td>";
					echo "<td class=\"" . check_multi_rate(($gb_split), .8, .6) . "\">" . $gb_split . "</td>";
					//echo "<td>" . $rs['gb_fb_ratio'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['sb_rate']), .015, 0) . "\">" . $rs['sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_sb_rate']), .015, 0) . "\">" . $rs['opp_sp_sb_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['k_rate']),.15, .25) . "\">" . $rs['k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_k_rate']), .15, .25) . "\">" . $rs['opp_sp_k_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['hr_rate']), .045 , .028) . "\">" . $rs['hr_rate'] . "</td>";
					echo "<td class=\"" . check_multi_rate(($rs['opp_sp_hr_rate']), .045, .028) . "\">" . $rs['opp_sp_hr_rate'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['adi']), 61) . "\">" . $rs['adi'] . "</td>";
					echo "<td class=\"" . $wind_direction . "\">" . $rs['wind_direction'] . "</td>";
					echo "<td class=\"" . check_rate(($rs['wind_speed']), 8) . "\">" . $rs['wind_speed'] . "</td>";
					echo "<td class=\"" . check_sub_rate(($rs['pop']), 25) . "\">" . $rs['pop'] . "%</td>";
					echo "</tr>";
			}
		}
		echo "</table>";
		vd($teams);
		//$vs_splits = lookup_batter_vs_pitcher($vs_id);
	}
	else
	{
	}
}
else
{
	echo "<table id=\"teamtable\">";
	echo "<tr>";
	$sql = "SELECT *, a.location as game_location, d.k_per_pa as k_per_pa, a.team_name as home_team FROM tbl_mlb_game_data a, v_pitcher_team_stats c, v_team_stats d, tbl_salaries e WHERE e.probable = 'Yes' AND a.team_sp_name LIKE CONCAT('% ', last_name) AND e.game_date = a.game_date AND a.opponent = d.team_name AND a.season = d.season AND a.team_name = c.team_name AND c.starting = 0 AND a.season = c.season AND a.gt >= " . $gt_start . " AND a.gt <= " . $gt_end . " ORDER BY a.game_date, a.gt, a.site asc, a.location DESC";	
	$sql = "SELECT *, a.opp_abv as opp, a.location as game_location, d.k_per_pa as k_per_pa, a.team_name as home_team, e.fd_salary as salary, e.nf_pts, e.nf_value, e.rg_pts, e.rg_value FROM tbl_mlb_game_data a, v_pitcher_team_stats c, v_team_stats d, tbl_player_stats e WHERE (a.team_sp_name = e.full_name OR (a.team_abv = e.team_abv AND a.team_sp_name LIKE CONCAT('%', e.last_name) AND e.pos = 'P')) AND e.pos = 'P' AND e.game_date = a.game_date AND a.opponent = d.team_name AND a.season = d.season AND a.team_name = c.team_name AND c.starting = 0 AND a.season = c.season AND a.gt >= " . $gt_start . " AND a.gt <= " . $gt_end . " ORDER BY a.game_date, a.gt, a.site asc, a.location DESC";	
	//$sql = "SELECT *, a.location as game_location, a.team_name as home_team, b.fd_salary as salary, b.nf_pts, b.nf_value, b.rg_pts, b.rg_value FROM tbl_mlb_game_data a, tbl_player_stats b WHERE (a.team_sp_name = b.full_name OR (a.team_abv = b.team_abv AND a.team_sp_name LIKE CONCAT('%', b.last_name) AND b.pos = 'P')) AND b.pos = 'P' AND b.game_date = a.game_date AND a.gt >= " . $gt_start . " AND a.gt <= " . $gt_end . " ORDER BY a.game_date, a.gt, a.site asc, a.location DESC";	
	//$sql = "SELECT *, a.location as game_location, d.k_per_pa as k_per_pa, a.team_name as home_team, e.fd_salary as salary FROM tbl_mlb_game_data a, v_pitcher_team_stats c, v_team_stats d, tbl_player_stats e WHERE a.team_sp_name = e.full_name AND e.game_date = a.game_date AND a.opponent = d.team_name AND a.season = d.season AND a.team_name = c.team_name AND c.starting = 0 AND a.season = c.season AND a.gt >= " . $gt_start . " AND a.gt <= " . $gt_end . " ORDER BY a.game_date, a.gt, a.site asc, a.location DESC";	
	$results = mysql_query($sql);
	e($sql);
	echo "<th align=\"left\" title=\"Team Name\">Team</td>";
	echo "<th align=\"left\" title=\"Starting pitcher\">Starter</td>";
	echo "<th align=\"left\" title=\"\">MS points</td>";
	echo "<th align=\"left\" title=\"\">NF points</td>";
	echo "<th align=\"left\" title=\"\">RG points</td>";
	echo "<th align=\"left\" title=\"\">AVG points</td>";
	echo "<th align=\"left\" title=\"Expected points to salary ratio.  Higher is better.\">MS Value</td>";
	echo "<th align=\"left\" title=\"Expected points to salary ratio.  Higher is better.\">NF Value</td>";
	echo "<th align=\"left\" title=\"Expected points to salary ratio.  Higher is better.\">RG Value</td>";
	echo "<th align=\"left\" title=\"Expected points to salary ratio.  Higher is better.\">AVG Value</td>";
	echo "<th align=\"left\" title=\"\">Salary</td>";
	echo "<th align=\"left\" title=\"Team's chance to win based on moneyline.\">MLW</td>";
	echo "<th align=\"left\" title=\"Starting pitcher current ERA\">2016 ERA</td>";
	echo "<th align=\"left\" title=\"Starting pitcher weighted ERA score.  The higher the better\">ERA Score</td>";
	echo "<th align=\"left\" title=\"Starting pitcher current season WHIP\">WHIP</td>";
	echo "<th align=\"left\" title=\"Team Name\">Opp</td>";
	echo "<th align=\"left\" title=\"Lineup predicted OPS based on batter splits of the opposing team\">Opp OPS</td>";
	echo "<th align=\"left\" title=\"Starting pitcher expected strikeouts\">Exp K</td>";
	echo "<th align=\"left\" title=\"Starting pitcher average IP per start\">Opp K/PA</td>";
	echo "<th align=\"left\" title=\"Starting pitcher expected strikeouts\">Exp K adj</td>";
	echo "<th align=\"left\" title=\"Starting pitcher average IP per start\">AVG IP</td>";
	echo "<th align=\"left\" title=\"Overall OPS\">Team OPS</td>";
	echo "<th align=\"left\" title=\"Total expected runs\">ExR Total</td>";
	echo "<th align=\"left\" title=\"Starting pitcher OPS based on actual batter platoon splits\">SP OPS</td>";
	echo "<th align=\"left\" title=\"Lineup platoon ratio.  Higher number indicates favorable batters for platoon matchups\">L-P ratio</td>";
	echo "<th align=\"left\" title=\"Starting pitcher ops vs RHB\">RHB</td>";
	echo "<th align=\"left\" title=\"Starting pitcher ops vs RHB\">RHB PF</td>";
	echo "<th align=\"left\" title=\"Starting pitcher ops vs LHB\">LHB</td>";
	echo "<th align=\"left\" title=\"Starting pitcher ops vs RHB\">LHB PF</td>";
	//echo "<th align=\"left\" title=\"Starting pitcher last season ERA\">2014 ERA</td>";
	echo "<th align=\"left\" title=\"Air Density index.  Higher equals dense air, balls travel less, pitches have more movement.\">ADI</td>";
	echo "<th align=\"left\" title=\"Wind direction relative to the park.  S is directly out, N is directly in.\">dir</td>";
	echo "<th align=\"left\" title=\"Wind speed at game start\">mph</td>";

	echo "</tr>";
	

	while($rs=mysql_fetch_assoc($results))
	{
		$lineup_hand_ratio = '-';

		$hs_throws = $rs['team_sp_throws'];
		$hs_name = $rs['team_sp_name'];
		$hs_id = $rs['team_sp'];
		
		$sql_sp = "SELECT * FROM v_pitcher_stats a WHERE a.season = '" . $year . "' AND a.`starting` = 1 AND a.player_id = '" . $hs_id . "'";
		$results_sp = mysql_query($sql_sp);
		//e($sql_sp);
		$k_per_9 = 0;
		$k_per_ip = 0;
		$k_per_ip_adj = 0;
		if(mysql_num_rows($results_sp) > 0)
		{
			$rs_sp = mysql_fetch_assoc($results_sp);
			$k_per_ip = ($rs_sp['k_per_9']/9);
			$k_per_ip_adj = ($rs_sp['k_per_9']/9)*($rs['k_per_pa']/.2)*($rs['k_per_pa']/.2);
		}
		else
		{		
			$sql_sp = "SELECT * FROM v_pitcher_stats a WHERE a.season = '" . ($year-1) . "' AND a.`starting` = 1 AND a.player_id = '" . $hs_id . "'";
			$results_sp = mysql_query($sql_sp);
			//e($sql_sp);
			$k_per_9 = 0;
			$k_per_ip = 0;
			$k_per_ip_adj = 0;
			if(mysql_num_rows($results_sp) > 0)
			{
				$rs_sp = mysql_fetch_assoc($results_sp);
				$k_per_ip = ($rs_sp['k_per_9']/9);
				$k_per_ip_adj = ($rs_sp['k_per_9']/9)*$rs['k_per_pa']/.2*$rs['k_per_pa']/.2;
			}
		}
		
		
		$hs_era = '*';
		$hs_ba = '*';
		$hs_ERA = '*';
		$pts_per_out = '*';
		$hs_era_score = '*';

		
		if($rs['game_location'] == 'home')
		{
			$team_ops = $rs['team_ops'] + .025;
			$opp_ops = $rs['opp_ops'] - .025;
		}
		if($rs['game_location'] == 'road')
		{
			$team_ops = $rs['team_ops'] - .025;
			$opp_ops = $rs['opp_ops'] + .025;
		}

		if($rs['game_location'] == 'home')
		{
			$total_score = (((($team_ops+$opp_ops)*9.5)-5.8));
		}
		else
		{
			$total_score = (((($team_ops+$opp_ops)*9.5)-5.8)/9)*5;
		}
		if($rs['team_sp_avg_ip'] == 0)
		{
			$team_sp_avg_ip = '5';
		}
		else
		{
			$team_sp_avg_ip = $rs['team_sp_avg_ip'];
			
		}
		if($rs['opp_sp_avg_ip'] == 0)
		{
			$opp_sp_avg_ip = '5';
		}
		else
		{
			$opp_sp_avg_ip = $rs['opp_sp_avg_ip'];
			
		}
		$team_starter_runs = ((($team_ops*9.5)-2.9)/9)*$opp_sp_avg_ip;
		$opp_starter_runs = ((($opp_ops*9.5)-2.9)/9)*$team_sp_avg_ip;
		$team_rp_expected_runs = ((9-$opp_sp_avg_ip)*($rs['opp_rp_era']/9));
		$opp_rp_expected_runs = ((9-$team_sp_avg_ip)*($rs['team_rp_era']/9));
		$team_runs = $team_starter_runs + $team_rp_expected_runs;
		$opp_runs = $opp_starter_runs + $opp_rp_expected_runs;
		$sp_points = ((($team_sp_avg_ip * ($k_per_ip_adj)) + $team_sp_avg_ip - $opp_starter_runs + ($rs['mlw']*4))*3);
		$avg_pts = ($sp_points + $rs['nf_pts'] + $rs['rg_pts'])/3;
		$avg_val = ($sp_points + $rs['nf_pts'] + $rs['rg_pts'])/((($rs['salary']/1000)*3));
		$suggested_unit = 0;
		$suggested_bet = 0;
		if($rs['game_location'] == 'home')
		{
			$total_score = $team_runs + $opp_runs;
			if($total_score > $rs['over'])
			{
				/*
				$suggested_unit = 1;
				$suggested_bet = $suggested_unit * $unit;
				//$suggested_bet = 10;
				//if($suggested_bet == 1)
				//	$suggested_bet = 0;
				$return_rate = "high";
				$sb_risk += abs($rs['over_winnings']) * $suggested_bet;
				$sb_winnings += $rs['over_winnings'] * $suggested_bet;	
				*/
			}
		}
		else
		{
			$total_score = (($team_runs + $opp_runs)/9)*5;
		}
		$avg_pts = ($sp_points + $rs['nf_pts'] + $rs['rg_pts'])/3;
		$sp_check = '';
		if($sp_points > 9 && $rs['opp_lineup_ops'] < .68 && $rs['k_per_pa'] > .21)
			$sp_check = 'high';
		echo "<tr align=\"left\">";
		echo "<td align=\"left\" class=\"\">" . $rs['team_abv'] . "</td>";
		echo "<td class=\"" . check_multi_rate(($avg_pts), 40, 30) . "\"><a href=\"http://www.baseball-reference.com/players/" . (substr($hs_id, 0,1)) . "/" . $hs_id . ".shtml\" title=\"" . $hs_era . "/" . $hs_whip . "/" . $hs_baopp . "\" target=\"new\">" . stripslashes($hs_name) . "(" . $hs_throws . ")</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($sp_points), 30, 20) . "\">" . round($sp_points,1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['nf_pts']), 35, 30) . "\">" . round($rs['nf_pts'],1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['rg_pts']), 35, 30) . "\">" . round($rs['rg_pts'],1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($avg_pts), 30, 20) . "\">" . round($avg_pts,1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($sp_points/($rs['salary']/1000)), 4,3.5) . "\">" . round($sp_points/($rs['salary']/1000),2) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['nf_value']), 4, 3.5) . "\">" . round($rs['nf_value'],1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['rg_value']), 4.5, 4) . "\">" . round($rs['rg_value'],1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($avg_val), 4, 3) . "\">" . round($avg_val,1) . "</td>";
		echo "<td align=\"left\" class=\"\">" . ($rs['salary']/1000) . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['mlw']), .6, .4) . "\">" . round($rs['mlw'],2) . "</td>";
		echo "<td align=\"left\" class=\"" . check_sub_rate(($rs['team_sp_era']), 3.77) . "\">" . number_format($rs['team_sp_era'],2) . "era</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['team_sp_era_score']), 1.2, .8) . "\">" . number_format($rs['team_sp_era_score'],2) . "e+</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['team_sp_whip']), 1.1, 1.3) . "\">" . number_format($rs['team_sp_whip'],2) . "whip</td>";
		echo "<td align=\"left\" class=\"\">" . $rs['opp'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['opp_lineup_ops']), .7, .75) . "\">" . $rs['opp_lineup_ops'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_rate(($k_per_ip), .8) . "\">" . number_format($k_per_ip*$team_sp_avg_ip,1) . "K</td>";
		echo "<td align=\"left\" class=\"" . check_multi_rate(($rs['k_per_pa']), .21, .19) . "\">" . number_format($rs['k_per_pa'],3) . "k/pa</td>";
		echo "<td align=\"left\" class=\"" . check_rate(($k_per_ip_adj), .8) . "\">" . number_format($k_per_ip_adj*$team_sp_avg_ip,1) . "K</td>";
		echo "<td align=\"left\" class=\"" . check_rate(($team_sp_avg_ip), 5) . "\">" . number_format($team_sp_avg_ip,1) . "ip</td>";
		echo "<td align=\"left\" class=\"" . check_rate($team_ops, $opp_ops) . "\">" . number_format($team_ops,3) . "</td>";
		echo "<td align=\"left\" class=\"" . check_rate($team_runs, $opp_runs) . "\">" . number_format($team_runs,1) . "</td>";
		echo "<td align=\"left\" class=\"" . check_sub_rate(($rs['team_sp_ops']), .714) . "\">" . $rs['team_sp_ops'] . "</td>";
		echo "<td align=\"left\" class=\"" . $sb_rate . "\">" . $rs['team_sp_platoon_ratio'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_sub_rate(($rs['team_sp_ops_rhb']), .714) . "\">" . $rs['team_sp_ops_rhb'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_rate(($rs['park_factor_rhb']), 1) . "\">" . $rs['park_factor_rhb'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_sub_rate(($rs['team_sp_ops_lhb']), .714) . "\">" . $rs['team_sp_ops_lhb'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_rate(($rs['park_factor_lhb']), 1) . "\">" . $rs['park_factor_lhb'] . "</td>";
		//echo "<td align=\"left\" class=\"" . check_sub_rate(($rs['team_sp_last_era']), 3.77) . "\">" . number_format($rs['team_sp_last_era'],2) . "e</td>";
		echo "<td align=\"left\" class=\"" . check_sub_rate(($rs['adi']), 61) . "\">" . $rs['adi'] . "</td>";
		echo "<td align=\"left\" class=\"" . $wind_direction . "\">" . $rs['wind_direction'] . "</td>";
		echo "<td align=\"left\" class=\"" . check_rate(($rs['wind_speed']), 8) . "\">" . $rs['wind_speed'] . "</td>";
		echo "</tr>";
	}
}

echo "<p>Completed</p>";

?>


</body>
</html>
