import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {Config} from '@remotion/cli/config';

const localBrowser = resolve(
  process.cwd(),
  '..',
  '.runtime',
  `chrome-headless-shell-${process.platform}-${process.arch}`,
  'chrome-headless-shell',
);

if (existsSync(localBrowser)) {
  Config.setBrowserExecutable(localBrowser);
}
