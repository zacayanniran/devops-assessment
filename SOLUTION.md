SOLUTION.md
What I changed and why
a. Moved writes out of the request path
The original /api/data endpoint performed 5 reads and 5 writes directly against MongoDB.
Under high load (5,000 VUs), this caused MongoDB to hit its IOPS limit and stall.
I changed the application so that:
The 5 reads still happen synchronously
The 5 writes are published to Google Pub/Sub Emulator
A separate worker consumes messages and performs batched MongoDB inserts
This reduces the number of synchronous write operations hitting MongoDB and smooths the load during peaks.
b. Added Pub/Sub emulator to the cluster
I deployed the Google Pub/Sub Emulator inside Kubernetes so the app and worker can communicate without leaving the cluster.
I also added a Job that creates the topic (writes-topic) and the subscription (writes-sub) each time the cluster is brought up.
c. Added a worker service
A new worker reads from the Pub/Sub subscription and writes to MongoDB in batches.
This keeps MongoDB from being overloaded by concurrent requests.
d. Tuned MongoDB access
Limited connection pool sizes
Added short timeouts
Used insert_many(..., ordered=False) for better throughput
e. Scaled the application
Scaled the application to several replicas so it can handle more incoming requests even when MongoDB is under pressure.
2. What bottlenecks I found and how I diagnosed them
a. MongoDB IOPS bottleneck
The assessment notes that MongoDB is limited to ~100 IOPS.
The default app generated far more writes during load tests.
I confirmed this by checking:
High latency in /api/data
Failed readiness/liveness probes
Error logs showing slow or timed‑out DB operations
b. Pod readiness failures
App pods frequently showed READY 0/1 because the readiness probe failed whenever MongoDB stalled.
c. Worker design missing
The app was doing all writes synchronously, so nothing was offloading those operations.
This made the app block on MongoDB for almost every request.
d. Cluster saturation under load
Running k6 at 5,000 VUs quickly caused:
High request duration
Increased failure rate
Pods restarting or failing readiness checks
Moving the write load to Pub/Sub fixed the majority of these issues.
3. Trade‑offs considered but not used
a. Redis instead of Pub/Sub
Considered Redis lists or streams for queuing.
I did not implement Redis because the assessment guide specifically encourages the Pub/Sub Emulator approach.
b. Caching layer
A cache (Redis or local memory) could reduce read load, but reads were not the primary bottleneck.
Most failures were caused by write pressure on MongoDB.
c. Rewriting the API to reduce the number of DB operations
The assessment states the 5 reads and 5 writes cannot be changed, so I kept them.
d. Scaling MongoDB
Not allowed by assessment rules, so only the application layer was scaled.

Please see the screenshots folder for the screenshots.