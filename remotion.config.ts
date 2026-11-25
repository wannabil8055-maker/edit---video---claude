import {Config} from '@remotion/cli/config';
import {existsSync} from 'fs';

// Cloud container: Remotion can't download its own Chrome (remotion.media is blocked),
// so use the preinstalled headless shell when it exists.
const HEADLESS_SHELL =
  '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (existsSync(HEADLESS_SHELL)) {
  Config.setBrowserExecutable(HEADLESS_SHELL);
}
