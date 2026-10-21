package com.rulesstudy.app

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.app.DownloadManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.IntentFilter
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

/**
 * Rules Study: the whole course runs from the bundled page in assets/index.html.
 * This activity only adds what a web page can't do on its own offline:
 * Android's microphone (SpeechRecognizer) and voices (TextToSpeech).
 * It goes online only to check GitHub for a newer version of itself and to download it.
 */
class MainActivity : Activity() {

    private lateinit var web: WebView
    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private var recognizer: SpeechRecognizer? = null
    private var pendingMicLang: String? = null

    @SuppressLint("SetJavaScriptEnabled", "AddJavascriptInterface")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this)
        setContentView(web)

        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true // keeps progress and settings
        web.webChromeClient = WebChromeClient()
        web.webViewClient = object : WebViewClient() {
            // Stay inside the app; never navigate to other pages.
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean = true
        }
        web.addJavascriptInterface(Bridge(), "AndroidBridge")

        if (savedInstanceState != null) web.restoreState(savedInstanceState)
        else web.loadUrl("file:///android_asset/index.html")

        tts = TextToSpeech(this) { status ->
            ttsReady = status == TextToSpeech.SUCCESS
            tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String?) {}
                override fun onDone(utteranceId: String?) = finished(utteranceId)
                @Deprecated("Deprecated in Java")
                override fun onError(utteranceId: String?) = finished(utteranceId)
            })
        }
    }

    private fun finished(utteranceId: String?) {
        if (utteranceId != null && utteranceId.endsWith("#last")) {
            js("window.onNativeSpeakDone(" + JSONObject.quote(utteranceId.removeSuffix("#last")) + ")")
        }
    }

    private fun js(code: String) = runOnUiThread { web.evaluateJavascript(code, null) }

    /** Called from the page as window.AndroidBridge.* */
    inner class Bridge {
        @JavascriptInterface fun speak(partsJson: String, id: String) = runOnUiThread { speakParts(partsJson, id) }
        @JavascriptInterface fun stopSpeaking() = runOnUiThread { tts?.stop() }
        @JavascriptInterface fun startListening(lang: String) = runOnUiThread { startMic(lang) }
        @JavascriptInterface fun stopListening() = runOnUiThread { recognizer?.stopListening() }
        @JavascriptInterface fun listVoices(lang: String): String = listVoicesJson(lang)
        @JavascriptInterface fun appVersion(): String = currentVersion().toString()
        @JavascriptInterface fun checkUpdate() = checkForUpdate()
        @JavascriptInterface fun installUpdate() = runOnUiThread { downloadUpdate() }
        @JavascriptInterface fun exitApp() = runOnUiThread { tts?.stop(); finishAndRemoveTask() }
    }

    // ---------- Reading aloud ----------
    private fun speakParts(partsJson: String, id: String) {
        val engine = tts
        if (engine == null || !ttsReady) {
            js("window.onNativeSpeakError('no-tts')"); js("window.onNativeSpeakDone(" + JSONObject.quote(id) + ")"); return
        }
        engine.stop()
        val parts = JSONArray(partsJson)
        var queuedLast = false
        var warnedHebrew = false
        for (i in 0 until parts.length()) {
            val part = parts.getJSONObject(i)
            val lang = part.getString("lang")
            engine.setSpeechRate(part.optDouble("rate", 0.9).toFloat())
            val voice = pickVoice(engine, lang, part.optString("voice", ""))
            if (voice != null) {
                engine.voice = voice
            } else {
                val result = engine.setLanguage(Locale.forLanguageTag(lang))
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    if (lang.startsWith("he") && !warnedHebrew) { js("window.onNativeSpeakError('he-missing')"); warnedHebrew = true }
                    continue
                }
            }
            val last = i == parts.length() - 1
            engine.speak(part.getString("text"), TextToSpeech.QUEUE_ADD, null, if (last) "$id#last" else "$id#$i")
            if (last) queuedLast = true
        }
        if (!queuedLast) js("window.onNativeSpeakDone(" + JSONObject.quote(id) + ")")
    }

    /** Voices for a language; Hebrew can be reported as "he" or the old code "iw". */
    private fun voicesFor(engine: TextToSpeech, lang: String): List<Voice> {
        val want = Locale.forLanguageTag(lang).language
        val codes = if (want == "he" || want == "iw") setOf("he", "iw") else setOf(want)
        return try { engine.voices?.filter { it.locale.language in codes }.orEmpty() } catch (e: Exception) { emptyList() }
    }
    private fun installed(v: Voice) = v.features?.contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED) != true

    /** The voice the person picked, or else the highest-quality installed voice for the language. */
    private fun pickVoice(engine: TextToSpeech, lang: String, name: String): Voice? {
        val list = voicesFor(engine, lang)
        if (name.isNotEmpty()) list.firstOrNull { it.name == name }?.let { return it }
        return list.filter { installed(it) }
            .sortedWith(compareByDescending<Voice> { it.quality }.thenBy { it.isNetworkConnectionRequired })
            .firstOrNull()
    }

    private fun listVoicesJson(lang: String): String {
        val engine = tts ?: return "[]"
        val arr = JSONArray()
        voicesFor(engine, lang).sortedByDescending { it.quality }.forEach {
            arr.put(JSONObject().put("name", it.name).put("quality", it.quality)
                .put("network", it.isNetworkConnectionRequired).put("installed", installed(it)))
        }
        return arr.toString()
    }

    // ---------- Microphone ----------
    private fun startMic(lang: String) {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            pendingMicLang = lang
            requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), REQ_MIC)
            return
        }
        if (!SpeechRecognizer.isRecognitionAvailable(this)) { sendSpeech("error", "", "unavailable"); return }
        tts?.stop()
        recognizer?.destroy()
        val r = SpeechRecognizer.createSpeechRecognizer(this)
        recognizer = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) = sendSpeech("start", "", null)
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
            override fun onPartialResults(partialResults: Bundle?) {
                val text = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull().orEmpty()
                if (text.isNotEmpty()) sendSpeech("partial", text, null)
            }
            override fun onResults(results: Bundle?) {
                val text = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull().orEmpty()
                sendSpeech("final", text, null)
            }
            override fun onError(error: Int) {
                val code = when (error) {
                    SpeechRecognizer.ERROR_NO_MATCH -> "no-match"
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "no-speech"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "permission"
                    SpeechRecognizer.ERROR_NETWORK, SpeechRecognizer.ERROR_NETWORK_TIMEOUT, SpeechRecognizer.ERROR_SERVER -> "network"
                    12, 13 -> "language" // language not supported / not downloaded (Android 12+)
                    else -> "other"
                }
                sendSpeech("error", "", code)
            }
        })
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }
        r.startListening(intent)
    }

    private fun sendSpeech(type: String, text: String, error: String?) {
        val o = JSONObject().put("type", type).put("text", text)
        if (error != null) o.put("error", error)
        js("window.onNativeSpeech(" + o.toString() + ")")
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode != REQ_MIC) return
        val lang = pendingMicLang
        pendingMicLang = null
        if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED && lang != null) startMic(lang)
        else sendSpeech("error", "", "permission")
    }

    // ---------- Lifecycle ----------
    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        // Let the page close the helper first; otherwise leave the app.
        web.evaluateJavascript("(window.onNativeBack && window.onNativeBack()) ? '1' : '0'") { result ->
            if (result != "\"1\"") finish()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onPause() {
        super.onPause()
        if (recognizer != null) {
            recognizer?.cancel()
            sendSpeech("end", "", null)
        }
    }

    // ----- Updates from GitHub -----
    private val releaseBase = "https://github.com/morrisedery-eng/rules-study/releases/latest/download/"
    private var downloadId = -1L
    private val main = Handler(Looper.getMainLooper())

    private fun currentVersion(): JSONObject {
        @Suppress("DEPRECATION")
        val info = packageManager.getPackageInfo(packageName, 0)
        @Suppress("DEPRECATION")
        val code = if (Build.VERSION.SDK_INT >= 28) info.longVersionCode else info.versionCode.toLong()
        return JSONObject().put("versionCode", code).put("versionName", info.versionName ?: "")
    }

    private fun checkForUpdate() = Thread {
        val result = JSONObject().put("current", currentVersion())
        try {
            val c = URL(releaseBase + "version.json").openConnection() as HttpURLConnection
            c.connectTimeout = 10000; c.readTimeout = 10000; c.instanceFollowRedirects = true
            if (c.responseCode == 200) result.put("latest", JSONObject(c.inputStream.bufferedReader().readText()))
            else result.put("error", "http " + c.responseCode)
            c.disconnect()
        } catch (e: Exception) { result.put("error", e.javaClass.simpleName) }
        js("window.onUpdateInfo && window.onUpdateInfo(" + result + ")")
    }.start()

    private fun downloadUpdate() {
        if (Build.VERSION.SDK_INT >= 26 && !packageManager.canRequestPackageInstalls()) {
            // Android asks once: allow this app to install its own updates.
            startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
            js("window.onUpdateStatus && window.onUpdateStatus('permission')"); return
        }
        val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "RulesStudy-update.apk").delete()
        val req = DownloadManager.Request(Uri.parse(releaseBase + "RulesStudy.apk"))
            .setTitle("Rules Study update")
            .setMimeType("application/vnd.android.package-archive")
            .setDestinationInExternalFilesDir(this, Environment.DIRECTORY_DOWNLOADS, "RulesStudy-update.apk")
            .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE)
        downloadId = dm.enqueue(req)
        js("window.onUpdateStatus && window.onUpdateStatus('downloading', 0)")
        main.post(object : Runnable { override fun run() {
            val cur = dm.query(DownloadManager.Query().setFilterById(downloadId))
            if (!cur.moveToFirst()) { cur.close(); return }
            val status = cur.getInt(cur.getColumnIndexOrThrow(DownloadManager.COLUMN_STATUS))
            val got = cur.getLong(cur.getColumnIndexOrThrow(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR))
            val total = cur.getLong(cur.getColumnIndexOrThrow(DownloadManager.COLUMN_TOTAL_SIZE_BYTES))
            cur.close()
            when (status) {
                DownloadManager.STATUS_SUCCESSFUL -> {
                    js("window.onUpdateStatus && window.onUpdateStatus('installing')")
                    val uri = dm.getUriForDownloadedFile(downloadId)
                    val install = Intent(Intent.ACTION_VIEW).setDataAndType(uri, "application/vnd.android.package-archive")
                        .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
                    try { startActivity(install) } catch (e: Exception) { js("window.onUpdateStatus && window.onUpdateStatus('failed')") }
                }
                DownloadManager.STATUS_FAILED -> js("window.onUpdateStatus && window.onUpdateStatus('failed')")
                else -> {
                    val pct = if (total > 0) (got * 100 / total) else 0
                    js("window.onUpdateStatus && window.onUpdateStatus('downloading', $pct)")
                    main.postDelayed(this, 500)
                }
            }
        }})
    }

    override fun onDestroy() {
        tts?.shutdown()
        recognizer?.destroy()
        web.destroy()
        super.onDestroy()
    }

    companion object { private const val REQ_MIC = 7 }
}
