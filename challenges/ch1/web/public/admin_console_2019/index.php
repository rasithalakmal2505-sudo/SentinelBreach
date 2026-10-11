<?php
// Legacy admin console from an earlier dev iteration. Never removed, never
// linked from the current site - only discoverable via robots.txt.
// No authentication is applied here (this IS the vulnerability: an unlinked
// path was treated as "hidden" rather than access-controlled).

$flag = "SBB{robots_txt_never_lies}"; // organizer: replace before real deployment
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Legacy Admin Console (deprecated)</title>
<style>
  body { font-family: "Courier New", monospace; background:#111; color:#0f0; padding:2rem; }
  .note { border:1px solid #0f0; padding:1.2rem; max-width:640px; }
  h2 { color:#f00; }
</style>
</head>
<body>
  <div class="note">
    <h2>⚠ INTERNAL INCIDENT NOTE - DO NOT DISTRIBUTE</h2>
    <p><strong>Ref:</strong> NG-INC-2026-0311</p>
    <p><strong>From:</strong> SOC Duty Analyst</p>
    <p><strong>Subject:</strong> Legacy admin console re-discovered on public host</p>
    <p>
      This console was scheduled for decommission during the 2019 platform migration
      and was never removed from the production web root. It is not linked from any
      current page, but it is still reachable directly and was found referenced in the
      site's <code>robots.txt</code>. Flagging this as the likely initial foothold used
      in the ShadowTrace intrusion timeline.
    </p>
    <p><strong>Flag:</strong> <?= $flag ?></p>
  </div>
</body>
</html>
