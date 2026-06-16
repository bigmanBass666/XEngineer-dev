/**
 * mock_getusermedia.js — getUserMedia Hook Script
 *
 * Monkey-patches navigator.mediaDevices.getUserMedia to return a virtual
 * MediaStream powered by preloaded Float32 PCM data, enabling browser-level
 * E2E tests to run in headless environments without a real microphone.
 *
 * Usage (in browser console or via agent-browser eval):
 *   // Load this script first, then:
 *   window.__mockAudio.setAudio(float32Array).startFeeding();
 *   // Later:
 *   window.__mockAudio.stopFeeding();
 *   window.__mockAudio.getState();
 *
 * Implementation:
 *   - AudioContext.createMediaStreamDestination() produces the virtual MediaStream
 *   - ScriptProcessorNode(512, 0, 1) acts as a data generator (0 input, 1 output)
 *   - onaudioprocess fires every ~32ms (512 samples @ 16kHz), writing PCM data
 *   - feeding=false outputs silence; feeding=true pushes data at real-time rate
 *   - Data exhaustion auto-stops feeding
 */

(function () {
  'use strict';

  // --- Internal state (Audio) -------------------------------------------------
  var SAMPLE_RATE = 16000;
  var BUFFER_SIZE = 512; // 512 samples = 32ms at 16kHz

  var audioContext = null;
  var scriptProcessor = null;
  var destination = null;
  var virtualStream = null;

  var pcmData = null; // Float32Array — audio data to feed
  var pcmOffset = 0;  // current read position in pcmData
  var feeding = false; // whether actively pushing audio (vs silence)
  var started = false; // whether the generator node has been started

  // --- Internal state (Video) -------------------------------------------------
  var videoCanvas = null;
  var videoCtx = null;
  var videoStreamObj = null;
  var videoFrameIndex = 0;
  var videoFrameTimer = null;

  // --- Logger ---------------------------------------------------------------
  function log(msg) {
    if (typeof console !== 'undefined') {
      console.log('[mockAudio] ' + msg);
    }
  }

  // --- Ensure AudioContext is created ---------------------------------------
  function ensureContext() {
    if (!audioContext) {
      audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });
    }
    if (!destination) {
      destination = audioContext.createMediaStreamDestination();
    }
    if (!scriptProcessor) {
      // ScriptProcessorNode(512, 0, 1): 0 input channels, 1 output channel
      // This acts as a pure generator — it writes data, doesn't read.
      scriptProcessor = audioContext.createScriptProcessor(BUFFER_SIZE, 0, 1);
      scriptProcessor.onaudioprocess = onAudioProcess;
      scriptProcessor.connect(destination);
    }
    if (!virtualStream) {
      virtualStream = destination.stream;
    }
    return virtualStream;
  }

  // --- Generator callback: fires every ~32ms --------------------------------
  function onAudioProcess(e) {
    var output = e.outputBuffer.getChannelData(0);
    // output.length is always BUFFER_SIZE (512)

    if (feeding && pcmData && pcmOffset < pcmData.length) {
      // Push real audio data at real-time rate
      var remaining = pcmData.length - pcmOffset;
      var count = Math.min(output.length, remaining);

      for (var i = 0; i < count; i++) {
        output[i] = pcmData[pcmOffset + i];
      }
      pcmOffset += count;

      // Fill rest with silence if chunk partially overlaps
      for (var j = count; j < output.length; j++) {
        output[j] = 0;
      }

      // Auto-stop when data is exhausted
      if (pcmOffset >= pcmData.length) {
        feeding = false;
        log('All PCM data consumed, auto-stopped feeding.');
      }
    } else {
      // Output silence
      for (var k = 0; k < output.length; k++) {
        output[k] = 0;
      }
    }
  }

  // --- Resume AudioContext if suspended (browser autoplay policy) -----------
  function resumeContext() {
    if (audioContext && audioContext.state === 'suspended') {
      audioContext.resume();
      log('AudioContext resumed from suspended state.');
    }
  }

  // --- Public API exposed as window.__mockAudio -----------------------------
  window.__mockAudio = {
    /**
     * Set the Float32 PCM audio data to feed.
     * @param {Float32Array} data - PCM samples at 16kHz, mono
     * @returns {object} this (chainable)
     */
    setAudio: function (data) {
      if (!(data instanceof Float32Array)) {
        throw new Error('setAudio expects a Float32Array, got ' + typeof data);
      }
      pcmData = data;
      pcmOffset = 0;
      log('Audio data set: ' + data.length + ' samples (' + (data.length / SAMPLE_RATE * 1000).toFixed(1) + 'ms)');
      return this;
    },

    /**
     * Start feeding audio data to the virtual stream.
     * Must call setAudio() first.
     * @returns {object} this (chainable)
     */
    startFeeding: function () {
      if (!pcmData) {
        throw new Error('No audio data set. Call setAudio() first.');
      }
      ensureContext();
      resumeContext();
      pcmOffset = 0;
      feeding = true;
      started = true;
      log('Feeding started (' + (pcmData.length / SAMPLE_RATE * 1000).toFixed(1) + 'ms of audio)');
      return this;
    },

    /**
     * Stop feeding audio; virtual stream will output silence.
     * @returns {object} this (chainable)
     */
    stopFeeding: function () {
      feeding = false;
      log('Feeding stopped. Stream outputs silence.');
      return this;
    },

    /**
     * Get current state of the mock audio system.
     * @returns {object} state snapshot
     */
    getState: function () {
      return {
        started: started,
        feeding: feeding,
        hasData: pcmData !== null,
        dataLength: pcmData ? pcmData.length : 0,
        currentOffset: pcmOffset,
        remainingSamples: pcmData ? Math.max(0, pcmData.length - pcmOffset) : 0,
        contextState: audioContext ? audioContext.state : 'not_created',
        sampleRate: SAMPLE_RATE,
        bufferSize: BUFFER_SIZE,
      };
    },

    /**
     * Reset all state and release resources.
     */
    reset: function () {
      feeding = false;
      started = false;
      pcmData = null;
      pcmOffset = 0;
      if (scriptProcessor) {
        scriptProcessor.disconnect();
        scriptProcessor = null;
      }
      if (destination) {
        destination = null;
      }
      if (audioContext) {
        audioContext.close().catch(function () {});
        audioContext = null;
      }
      virtualStream = null;
      log('Reset complete.');
    },
  };

  // --- Ensure Video Stream (canvas-based) -----------------------------------
  function ensureVideoStream() {
    if (videoStreamObj) return videoStreamObj;

    // Create off-screen canvas
    videoCanvas = document.createElement('canvas');
    videoCanvas.width = 640;
    videoCanvas.height = 480;
    videoCtx = videoCanvas.getContext('2d');

    // Draw first frame
    drawVideoFrame(0);

    // Create captureStream at 0.5 fps (1 frame per 2s)
    videoStreamObj = videoCanvas.captureStream(0.5);
    log('Virtual video stream created (640x480, 0.5 fps from canvas)');

    // Rotate frames every 2s to trigger frontend simpleHash change detection
    var frames = (window.__mockVideoFrames || []);
    if (frames.length > 1) {
      videoFrameTimer = setInterval(function () {
        videoFrameIndex = (videoFrameIndex + 1) % frames.length;
        drawVideoFrame(videoFrameIndex);
      }, 2000);
    }

    return videoStreamObj;
  }

  function drawVideoFrame(index) {
    var frames = (window.__mockVideoFrames || []);
    if (frames.length === 0) {
      // No frame data — draw placeholder
      videoCtx.fillStyle = '#496D89';
      videoCtx.fillRect(0, 0, 640, 480);
      videoCtx.fillStyle = '#FFFFFF';
      videoCtx.font = '24px sans-serif';
      videoCtx.fillText('XEngineer Test Video', 50, 250);
      return;
    }

    var dataUrl = frames[index % frames.length];
    var img = new Image();
    img.onload = function () {
      videoCtx.drawImage(img, 0, 0, 640, 480);
    };
    img.src = dataUrl;
  }

  // --- Monkey-patch getUserMedia --------------------------------------------
  var originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);

  navigator.mediaDevices.getUserMedia = async function (constraints) {
    if (constraints && constraints.audio && constraints.video) {
      // Both audio and video requested — return combined MediaStream
      log('Intercepted getUserMedia({audio, video}) — returning combined virtual stream.');
      var audioStream = ensureContext();
      resumeContext();
      var videoStream = ensureVideoStream();
      var audioTrack = audioStream.getAudioTracks()[0];
      var videoTrack = videoStream.getVideoTracks()[0];
      if (audioTrack && videoTrack) {
        return new MediaStream([audioTrack, videoTrack]);
      }
      return audioStream;
    }
    if (constraints && constraints.audio) {
      log('Intercepted getUserMedia({audio: true}) — returning virtual stream.');
      var stream = ensureContext();
      resumeContext();
      return stream;
    }
    if (constraints && constraints.video) {
      log('Intercepted getUserMedia({video: true}) — returning virtual video stream.');
      return ensureVideoStream();
    }
    // For other constraints, delegate to original implementation
    return originalGetUserMedia(constraints);
  };

  log('getUserMedia hook installed. Virtual audio + video stream ready.');
  log('API: window.__mockAudio = { setAudio, startFeeding, stopFeeding, getState, reset }');
  log('API: window.__mockVideoFrames = [data:image/jpeg;base64,...] (set before camera starts)');
})();
