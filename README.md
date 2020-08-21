# OctoPrint-Procastinator

This plugin allows for a configurable time window, during which print jobs are put on hold ("procrastinating") and
the user is given (configurable) options for when to resume/start the print job.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/juergenpabel/OctoPrint-Procastinator/archive/master.zip

## Configuration

 * Time window: During which to put the job on-hold
 * Time options: Multiple time options (in addition to "now") when to start the print job

## FAQ

- [Are you aware of the spelling error?](#are-you-aware-of-the-spelling-error)
- [Why didn't you just implement a print job scheduling functionality?](#why-didnt-you-just-implement-a-print-job-scheduling-functionality)
- [Why don't you pause the print job (instead of locking it)?](#why-dont-you-pause-the-print-job-instead-of-locking-it)

### Are you aware of the spelling error?

The correct spelling is proc*r*astinator and yes, I am. But it did not occur to me until
after I had implemented the first working PoC and at that point I didn't feel like doing
all that work and than I forgot about it until registering it with the octoprint plugin
manager. Now, I am undecided whether I'll just leave it as is or correct it.
By the way: the very first reported issue was about this spelling error - leave a comment
there if it's of any relevance to you.

### Why didn't you just implement a print job scheduling functionality?

My main reason for pausing (not really, see next question) an already started printjob
is that I have some other scripts/logic set up on my printers to shutdown the raspberry
(and printer) if it's not doing anything for a while. This approach circumvents any
problems with those implementations.

### Why don't you pause the print job (instead of locking it)?

First of: The (current) implementation is that the still-just-starting print job is put
on hold by obtaining the lock of the print job and just not allowing it to transition
into the printing phase.
This prevents any state changes (to the print job) due to user interactions or other
causes. Since I didn't observe any side effects during development of this approach,
this is how it is. (I might implement a configurable alternative if so desired.)

