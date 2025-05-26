<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>

<head>
  <title>Observing Stats</title>
  <meta name="GENERATOR" content="Quanta Plus">
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body>

<table>
  <h2>Observing Stats thisDay</h2>
  <tbody>
    <?php
    if (file_exists('SourceStats_thisDay.png') || file_exists('SourceStats_A-UP_thisDay.png')) {
    ?>
        <tr>
        <td><A href=Weather_thisDay.png>
            <IMG src=Weather_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=ObsStats_thisDay.txt>
            <IMG src=ObsStats_Summary.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=SourceTypeStats_thisDay.png>
            <IMG src=SourceTypeStats_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=SourceTypeStatsPie_thisDay.png>
            <IMG src=SourceTypeStatsPie_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=SourceClassStats_thisDay.png>
            <IMG src=SourceClassStats_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=SourceClassStatsPie_thisDay.png>
            <IMG src=SourceClassStatsPie_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <?php
        if (file_exists('SourceStats_thisDay.png')) {
        ?>
            <td><A href=SourceStats_thisDay.png>
                <IMG src=SourceStats_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        <?php
        } else {
        ?>
            <td><A href=SourceStats_A-UP_thisDay.png>
                <IMG src=SourceStats_A-UP_thisDay.png width="400" height="380" align="left" border="0"></A></td>
            <td><A href=SourceStats_Z-DWN_thisDay.png>
                <IMG src=SourceStats_Z-DWN_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        <?php
        }
        ?>
        </tr>
        <tr>
        <td><A href=ObservingMode_thisDay.png>
            <IMG src=ObservingMode_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=RunType_thisDay.png>
            <IMG src=RunType_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=RA_dists_thisDay.png>
            <IMG src=RA_dists_thisDay.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
    <?php
    } else {
    ?>
        <h3>There are no source runs thisDay</h3>
    <?php
    }
    ?>
  </tbody>
</table>

<hr><hr>
<table>
  <h2>Observing Stats thisMonth (dark run)</h2>
  <tbody>
    <?php
    if (file_exists('SourceStats_thisMonth.png') || file_exists('SourceStats_A-UP_thisMonth.png')) {
    ?>
        <tr>
        <td><A href=Weather_thisMonth.png>
            <IMG src=Weather_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=ObsStats_thisMonth.txt>
            <IMG src=ObsStats_Summary.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=SourceTypeStats_thisMonth.png>
            <IMG src=SourceTypeStats_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=SourceTypeStatsPie_thisMonth.png>
            <IMG src=SourceTypeStatsPie_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=SourceClassStats_thisMonth.png>
            <IMG src=SourceClassStats_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=SourceClassStatsPie_thisMonth.png>
            <IMG src=SourceClassStatsPie_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <?php
        if (file_exists('SourceStats_thisMonth.png')) {
        ?>
            <td><A href=SourceStats_thisMonth.png>
                <IMG src=SourceStats_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        <?php
        } else {
        ?>
            <td><A href=SourceStats_A-UP_thisMonth.png>
                <IMG src=SourceStats_A-UP_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
            <td><A href=SourceStats_Z-DWN_thisMonth.png>
                <IMG src=SourceStats_Z-DWN_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        <?php
        }
        ?>
        </tr>
        <tr>
        <td><A href=ObservingMode_thisMonth.png>
            <IMG src=ObservingMode_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=RunType_thisMonth.png>
            <IMG src=RunType_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=RA_dists_thisMonth.png>
            <IMG src=RA_dists_thisMonth.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
    <?php
    } else {
    ?>
        <h3>There are no source runs thisMonth (yet)</h3>
    <?php
    }
    ?>
  </tbody>
</table>

<hr><hr>
<table>
  <h2>Observing Stats thisSeason</h2>
  <tbody>
    <?php
    if (file_exists('SourceStats_thisSeason.png') || file_exists('SourceStats_A-UP_thisSeason.png')) {
    ?>
        <tr>
        <td><A href=Weather_thisSeason.png>
            <IMG src=Weather_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=ObsStats_thisSeason.txt>
            <IMG src=ObsStats_Summary.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=SourceTypeStats_thisSeason.png>
            <IMG src=SourceTypeStats_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=SourceTypeStatsPie_thisSeason.png>
            <IMG src=SourceTypeStatsPie_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=SourceClassStats_thisSeason.png>
            <IMG src=SourceClassStats_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=SourceClassStatsPie_thisSeason.png>
            <IMG src=SourceClassStatsPie_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <?php
        if (file_exists('SourceStats_thisSeason.png')) {
        ?>
            <td><A href=SourceStats_thisSeason.png>
                <IMG src=SourceStats_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        <?php
        } else {
        ?>
            <td><A href=SourceStats_A-UP_thisSeason.png>
                <IMG src=SourceStats_A-UP_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
            <td><A href=SourceStats_Z-DWN_thisSeason.png>
                <IMG src=SourceStats_Z-DWN_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        <?php
        }
        ?>
        </tr>
        <tr>
        <td><A href=ObservingMode_thisSeason.png>
            <IMG src=ObservingMode_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        <td><A href=RunType_thisSeason.png>
            <IMG src=RunType_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
        <tr>
        <td><A href=RA_dists_thisSeason.png>
            <IMG src=RA_dists_thisSeason.png width="400" height="380" align="left" border="0"></A></td>
        </tr>
    <?php
    } else {
    ?>
        <h3>There are no source runs thisSeason (yet)</h3>
    <?php
    }
    ?>
  </tbody>
</table>

<hr><hr>
<table>
  <h2>Observing Stats Messages</h2>
  <tbody>
    <tr>
      <td><A href=ObsStats_Msgs.txt>
            <IMG src=ObsStats_Msgs.png width="200" height="190" align="left" border="0"></td>
     </tr>
  </tbody>
</table>

</body>
</html>
