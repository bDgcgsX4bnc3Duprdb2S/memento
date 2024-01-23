# TODO

- Load cache from disk to reuse cache between program calls.
  Load can be serial or // to importing module or can be trigerred only at first fun call.
  This cache must be written to disk before program exit.
  This cache must be cleared if fun signature change.

- Compute cache management duration (search and update).

- Make stats about speed improvment for each call and also for each fun.
