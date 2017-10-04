# MONROE - Mobi-QoE: QoE Measurements for YouTube

Quality of Experience (QoE) is a well-known concept in the networking research community, but its development
has been traditionally limited to laboratory studies. We are witnessing a growing demand from mobile operators
for more user-centric approaches to manage their networks in an increasingly competitive scenario. This need
has boosted the research interest in scaling QoE out of the lab, bringing it into the management of operational
networks. This combined industry/research growing interest in QoE-based solutions for network management
motivates the Mobi-QoE proposal.

Mobi-QoE proposes both to extend MONROE’s testbed with new software (SW) tools as well as conducting
innovative experiments. The first objective of Mobi-QoE is to extend MONROE’s testbed to the QoE domain, by
integrating novel SW-based QoE-capable measurement tools and QoE subjective-models to assess the
performance of MBB networks for popular end-user services (e.g., YouTube, Facebook, Spotify, etc.) from a user-
centric perspective. Such tools and models provide a multi-layer monitoring perspective, measuring QoE-
relevant features at the network and application layers, and forecasting end-user experience (e.g., MOS scores).

# Local Testing
Run simply the following command and get the results into a selected folder:

```
docker run --cap-add=NET_ADMIN --env LOCAL=1 -v <Path to result folder>:/monroe/results yomo_docker
```

or use a config file in addition to specify YouTube ID, duration and bitrates for different quality levels:

```
docker run --cap-add=NET_ADMIN --env LOCAL=1 -v <Path to config file>:/monroe/config -v <Path to result folder>:/monroe/results yomo_docker
```

# Output
The container will export three different log files:
  1. Information about the playout buffer (in intervals of approx. 1s) in the following format:
     ```
     timestamp#video playback time#buffered playback time#available playback time\n
     ```
  2. Information about the video player (playback events, video information) in the following format:
     ```
     timestamp#information\n
     ```
  3. Statistics about bitrate, buffer, and stallings
     ```
     avg, max, min, 25-50-75-90 quantiles of: bitrate [KB], buffer [s], number of stalls (only one value), duration of stalls
     ```
  4. Network traffic information during the video playback using tshark



