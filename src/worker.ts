import * as Comlink from 'comlink';
import { analyzeProfile } from './analyzer.ts';

const workerAPI = {
  analyzeProfile
};

Comlink.expose(workerAPI);
export type WorkerAPI = typeof workerAPI;
