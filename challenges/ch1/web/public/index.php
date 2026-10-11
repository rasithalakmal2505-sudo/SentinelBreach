<?php
// NovaGrid Utilities - Employee Portal (decoy front-end)
// This page is intentionally "properly secured" - the real issue is an
// unlinked legacy admin path, not this login form. No auth bypass exists here.

$db = function_exists('mysqli_connect')
    ? @mysqli_connect(getenv('DB_HOST'), getenv('DB_USER'), getenv('DB_PASS'), getenv('DB_NAME'))
    : null;
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $user = $_POST['username'] ?? '';
    $pass = $_POST['password'] ?? '';

    if ($db) {
        $stmt = $db->prepare("SELECT id FROM employees WHERE username = ? AND password_hash = SHA2(?, 256)");
        $stmt->bind_param('ss', $user, $pass);
        $stmt->execute();
        $stmt->store_result();
        if ($stmt->num_rows === 1) {
            $error = "Login OK, but this portal has no further employee-facing content in this exercise.";
        } else {
            $error = "Invalid username or password.";
        }
    } else {
        $error = "Service temporarily unavailable.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>NovaGrid Utilities - Employee Portal</title>
<style>
  body { font-family: Arial, sans-serif; background:#0d1b2a; color:#e0e1dd; display:flex;
         align-items:center; justify-content:center; height:100vh; margin:0; }
  .card { background:#1b263b; padding:2.5rem; border-radius:8px; width:320px; box-shadow:0 4px 20px rgba(0,0,0,.4); }
  h1 { font-size:1.2rem; margin-top:0; color:#e0e1dd; }
  input { width:100%; padding:.6rem; margin:.4rem 0; border-radius:4px; border:1px solid #415a77;
          background:#0d1b2a; color:#e0e1dd; box-sizing:border-box; }
  button { width:100%; padding:.6rem; margin-top:.8rem; border:none; border-radius:4px;
           background:#4cc9f0; color:#0d1b2a; font-weight:bold; cursor:pointer; }
  .msg { font-size:.85rem; margin-top:1rem; color:#f4a261; }
  footer { font-size:.7rem; color:#778da9; margin-top:1.5rem; text-align:center; }
</style>
</head>
<body>
  <div class="card">
    <h1>NovaGrid Utilities &mdash; Employee Portal</h1>
    <form method="POST">
      <input type="text" name="username" placeholder="Username" required>
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit">Sign In</button>
    </form>
    <?php if ($error): ?><div class="msg"><?= htmlspecialchars($error) ?></div><?php endif; ?>
    <footer>NovaGrid Internal Systems &copy; 2019-2026</footer>
  </div>
</body>
</html>
