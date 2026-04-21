"use strict";var Tt=Object.create;var w=Object.defineProperty;var ht=Object.getOwnPropertyDescriptor;var ft=Object.getOwnPropertyNames;var bt=Object.getPrototypeOf,Ot=Object.prototype.hasOwnProperty;var St=(r,e)=>{for(var t in e)w(r,t,{get:e[t],enumerable:!0})},re=(r,e,t,s)=>{if(e&&typeof e=="object"||typeof e=="function")for(let n of ft(e))!Ot.call(r,n)&&n!==t&&w(r,n,{get:()=>e[n],enumerable:!(s=ht(e,n))||s.enumerable});return r};var C=(r,e,t)=>(t=r!=null?Tt(bt(r)):{},re(e||!r||!r.__esModule?w(t,"default",{value:r,enumerable:!0}):t,r)),It=r=>re(w({},"__esModule",{value:!0}),r);var $t={};St($t,{generateContext:()=>se});module.exports=It($t);var _t=C(require("path"),1),Et=require("os"),gt=require("fs");var me=require("bun:sqlite");var b=require("path"),ae=require("os"),P=require("fs");var de=require("url");var R=require("fs"),U=require("path"),ie=require("os");var ne="bugfix,feature,refactor,discovery,decision,change",oe="how-it-works,why-it-exists,what-changed,problem-solution,gotcha,pattern,trade-off";var A=class{static DEFAULTS={CLAUDE_PILOT_MODEL:"haiku",CLAUDE_PILOT_CONTEXT_OBSERVATIONS:"50",CLAUDE_PILOT_WORKER_PORT:"41777",CLAUDE_PILOT_WORKER_HOST:"127.0.0.1",CLAUDE_PILOT_WORKER_BIND:"127.0.0.1",CLAUDE_PILOT_SKIP_TOOLS:"ListMcpResourcesTool,SlashCommand,Skill,TodoWrite,AskUserQuestion",CLAUDE_PILOT_DATA_DIR:(0,U.join)((0,ie.homedir)(),".pilot/memory"),CLAUDE_PILOT_LOG_LEVEL:"INFO",CLAUDE_PILOT_PYTHON_VERSION:"3.12",CLAUDE_CODE_PATH:"",CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS:!1,CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS:!1,CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT:!1,CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT:!1,CLAUDE_PILOT_CONTEXT_OBSERVATION_TYPES:ne,CLAUDE_PILOT_CONTEXT_OBSERVATION_CONCEPTS:oe,CLAUDE_PILOT_CONTEXT_FULL_COUNT:"10",CLAUDE_PILOT_CONTEXT_FULL_FIELD:"facts",CLAUDE_PILOT_CONTEXT_SESSION_COUNT:"10",CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY:!0,CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE:!0,CLAUDE_PILOT_FOLDER_CLAUDEMD_ENABLED:!1,CLAUDE_PILOT_FOLDER_MD_EXCLUDE:"[]",CLAUDE_PILOT_CHROMA_ENABLED:!0,CLAUDE_PILOT_VECTOR_DB:"chroma",CLAUDE_PILOT_EMBEDDING_MODEL:"Xenova/all-MiniLM-L6-v2",CLAUDE_PILOT_EXCLUDE_PROJECTS:"[]",CLAUDE_PILOT_REMOTE_TOKEN:"",CLAUDE_PILOT_RETENTION_ENABLED:!0,CLAUDE_PILOT_RETENTION_MAX_AGE_DAYS:"31",CLAUDE_PILOT_RETENTION_MAX_COUNT:"5000",CLAUDE_PILOT_RETENTION_EXCLUDE_TYPES:'["summary"]',CLAUDE_PILOT_RETENTION_SOFT_DELETE:!1,CLAUDE_PILOT_BATCH_SIZE:"5",CLAUDE_PILOT_VECTOR_DB_MAX_PHYSICAL_MB:"2048",CLAUDE_PILOT_VECTOR_DB_MAX_LOGICAL_MB:"51200"};static getAllDefaults(){return{...this.DEFAULTS}}static get(e){return this.DEFAULTS[e]}static getInt(e){let t=this.get(e);return parseInt(t,10)}static getBool(e){return this.get(e)==="true"}static loadFromFile(e){try{if(!(0,R.existsSync)(e)){let a=this.getAllDefaults();try{let c=(0,U.dirname)(e);(0,R.existsSync)(c)||(0,R.mkdirSync)(c,{recursive:!0}),(0,R.writeFileSync)(e,JSON.stringify(a,null,2),"utf-8"),console.log("[SETTINGS] Created settings file with defaults:",e)}catch(c){console.warn("[SETTINGS] Failed to create settings file, using in-memory defaults:",e,c)}return a}let t=(0,R.readFileSync)(e,"utf-8"),s=JSON.parse(t),n=s;if(s.env&&typeof s.env=="object"){n=s.env;try{(0,R.writeFileSync)(e,JSON.stringify(n,null,2),"utf-8"),console.log("[SETTINGS] Migrated settings file from nested to flat schema:",e)}catch(a){console.warn("[SETTINGS] Failed to auto-migrate settings file:",e,a)}}let o=["CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS","CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS","CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT","CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT","CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY","CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE","CLAUDE_PILOT_FOLDER_CLAUDEMD_ENABLED","CLAUDE_PILOT_CHROMA_ENABLED","CLAUDE_PILOT_RETENTION_ENABLED","CLAUDE_PILOT_RETENTION_SOFT_DELETE"],i={...this.DEFAULTS},d=!1;for(let a of Object.keys(this.DEFAULTS))if(n[a]!==void 0)if(o.includes(a)){let c=n[a];typeof c=="string"?(i[a]=c==="true",d=!0):i[a]=c}else i[a]=n[a];if(d)try{(0,R.writeFileSync)(e,JSON.stringify(i,null,2),"utf-8"),console.log("[SETTINGS] Migrated boolean settings from strings to actual booleans:",e)}catch(a){console.warn("[SETTINGS] Failed to auto-migrate boolean settings:",e,a)}return i}catch(t){return console.warn("[SETTINGS] Failed to load settings, using defaults:",e,t),this.getAllDefaults()}}};var Nt={};function Rt(){return typeof __dirname<"u"?__dirname:(0,b.dirname)((0,de.fileURLToPath)(Nt.url))}var Ht=Rt(),y=A.get("CLAUDE_PILOT_DATA_DIR"),$=process.env.CLAUDE_CONFIG_DIR||(0,b.join)((0,ae.homedir)(),".claude"),Gt=(0,b.join)(y,"archives"),Yt=(0,b.join)(y,"logs"),Vt=(0,b.join)(y,"trash"),qt=(0,b.join)(y,"backups"),Kt=(0,b.join)(y,"modes"),Jt=(0,b.join)(y,"settings.json"),pe=(0,b.join)(y,"pilot-memory.db"),zt=(0,b.join)(y,"vector-db"),Qt=(0,b.join)($,"settings.json"),Zt=(0,b.join)($,"CLAUDE.md"),es=(0,b.join)($,".credentials.json"),yt=(0,b.join)($,"plugins"),ts=(0,b.join)(yt,"marketplaces","pilot");function ce(r){(0,P.mkdirSync)(r,{recursive:!0})}var N=require("fs"),D=require("path"),ue=require("os"),G=(o=>(o[o.DEBUG=0]="DEBUG",o[o.INFO=1]="INFO",o[o.WARN=2]="WARN",o[o.ERROR=3]="ERROR",o[o.SILENT=4]="SILENT",o))(G||{}),le=(0,D.join)((0,ue.homedir)(),".pilot/memory"),Y=class{level=null;useColor;logFilePath=null;logFileInitialized=!1;constructor(){this.useColor=process.stdout.isTTY??!1}ensureLogFileInitialized(){if(!this.logFileInitialized){this.logFileInitialized=!0;try{let e=(0,D.join)(le,"logs");(0,N.existsSync)(e)||(0,N.mkdirSync)(e,{recursive:!0});let t=new Date().toISOString().split("T")[0];this.logFilePath=(0,D.join)(e,`pilot-memory-${t}.log`)}catch(e){console.error("[LOGGER] Failed to initialize log file:",e),this.logFilePath=null}}}getLevel(){if(this.level===null)try{let e=(0,D.join)(le,"settings.json");if((0,N.existsSync)(e)){let t=(0,N.readFileSync)(e,"utf-8"),n=(JSON.parse(t).CLAUDE_PILOT_LOG_LEVEL||"INFO").toUpperCase();this.level=G[n]??1}else this.level=1}catch{this.level=1}return this.level}correlationId(e,t){return`obs-${e}-${t}`}sessionId(e){return`session-${e}`}formatData(e){if(e==null)return"";if(typeof e=="string")return e;if(typeof e=="number"||typeof e=="boolean")return e.toString();if(typeof e=="object"){if(e instanceof Error)return this.getLevel()===0?`${e.message}
${e.stack}`:e.message;if(Array.isArray(e))return`[${e.length} items]`;let t=Object.keys(e);return t.length===0?"{}":t.length<=3?JSON.stringify(e):`{${t.length} keys: ${t.slice(0,3).join(", ")}...}`}return String(e)}formatTool(e,t){if(!t)return e;let s=t;if(typeof t=="string")try{s=JSON.parse(t)}catch{s=t}if(e==="Bash"&&s.command)return`${e}(${s.command})`;if(s.file_path)return`${e}(${s.file_path})`;if(s.notebook_path)return`${e}(${s.notebook_path})`;if(e==="Glob"&&s.pattern)return`${e}(${s.pattern})`;if(e==="Grep"&&s.pattern)return`${e}(${s.pattern})`;if(s.url)return`${e}(${s.url})`;if(s.query)return`${e}(${s.query})`;if(e==="Task"){if(s.subagent_type)return`${e}(${s.subagent_type})`;if(s.description)return`${e}(${s.description})`}return e==="Skill"&&s.skill?`${e}(${s.skill})`:e==="LSP"&&s.operation?`${e}(${s.operation})`:e}formatTimestamp(e){let t=e.getFullYear(),s=String(e.getMonth()+1).padStart(2,"0"),n=String(e.getDate()).padStart(2,"0"),o=String(e.getHours()).padStart(2,"0"),i=String(e.getMinutes()).padStart(2,"0"),d=String(e.getSeconds()).padStart(2,"0"),a=String(e.getMilliseconds()).padStart(3,"0");return`${t}-${s}-${n} ${o}:${i}:${d}.${a}`}log(e,t,s,n,o){if(e<this.getLevel())return;this.ensureLogFileInitialized();let i=this.formatTimestamp(new Date),d=G[e].padEnd(5),a=t.padEnd(6),c="";n?.correlationId?c=`[${n.correlationId}] `:n?.sessionId&&(c=`[session-${n.sessionId}] `);let l="";o!=null&&(o instanceof Error?l=this.getLevel()===0?`
${o.message}
${o.stack}`:` ${o.message}`:this.getLevel()===0&&typeof o=="object"?l=`
`+JSON.stringify(o,null,2):l=" "+this.formatData(o));let m="";if(n){let{sessionId:E,memorySessionId:T,correlationId:O,..._}=n;Object.keys(_).length>0&&(m=` {${Object.entries(_).map(([h,I])=>`${h}=${I}`).join(", ")}}`)}let g=`[${i}] [${d}] [${a}] ${c}${s}${m}${l}`;if(this.logFilePath)try{(0,N.appendFileSync)(this.logFilePath,g+`
`,"utf8")}catch(E){process.stderr.write(`[LOGGER] Failed to write to log file: ${E}
`)}else process.stderr.write(g+`
`)}debug(e,t,s,n){this.log(0,e,t,s,n)}info(e,t,s,n){this.log(1,e,t,s,n)}warn(e,t,s,n){this.log(2,e,t,s,n)}error(e,t,s,n){this.log(3,e,t,s,n)}dataIn(e,t,s,n){this.info(e,`\u2192 ${t}`,s,n)}dataOut(e,t,s,n){this.info(e,`\u2190 ${t}`,s,n)}success(e,t,s,n){this.info(e,`\u2713 ${t}`,s,n)}failure(e,t,s,n){this.error(e,`\u2717 ${t}`,s,n)}timing(e,t,s,n){this.info(e,`\u23F1 ${t}`,n,{duration:`${s}ms`})}happyPathError(e,t,s,n,o=""){let c=((new Error().stack||"").split(`
`)[2]||"").match(/at\s+(?:.*\s+)?\(?([^:]+):(\d+):(\d+)\)?/),l=c?`${c[1].split("/").pop()}:${c[2]}`:"unknown",m={...s,location:l};return this.warn(e,`[HAPPY-PATH] ${t}`,m,n),o}},u=new Y;var F=class{db;constructor(e=pe){e!==":memory:"&&ce(y),this.db=new me.Database(e),this.db.run("PRAGMA journal_mode = WAL"),this.db.run("PRAGMA synchronous = NORMAL"),this.db.run("PRAGMA foreign_keys = ON"),this.initializeSchema(),this.ensureWorkerPortColumn(),this.ensurePromptTrackingColumns(),this.removeSessionSummariesUniqueConstraint(),this.addObservationHierarchicalFields(),this.makeObservationsTextNullable(),this.createUserPromptsTable(),this.ensureDiscoveryTokensColumn(),this.createPendingMessagesTable(),this.renameSessionIdColumns(),this.repairSessionIdColumnRename(),this.addFailedAtEpochColumn(),this.ensureSessionPlansTable(),this.createProjectRootsTable(),this.ensureNotificationsTable()}initializeSchema(){this.db.run(`
      CREATE TABLE IF NOT EXISTS schema_versions (
        id INTEGER PRIMARY KEY,
        version INTEGER UNIQUE NOT NULL,
        applied_at TEXT NOT NULL
      )
    `);let e=this.db.prepare("SELECT version FROM schema_versions ORDER BY version").all();(e.length>0?Math.max(...e.map(s=>s.version)):0)===0&&(u.info("DB","Initializing fresh database with migration004"),this.db.run(`
        CREATE TABLE IF NOT EXISTS sdk_sessions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          content_session_id TEXT UNIQUE NOT NULL,
          memory_session_id TEXT UNIQUE,
          project TEXT NOT NULL,
          user_prompt TEXT,
          started_at TEXT NOT NULL,
          started_at_epoch INTEGER NOT NULL,
          completed_at TEXT,
          completed_at_epoch INTEGER,
          status TEXT CHECK(status IN ('active', 'completed', 'failed')) NOT NULL DEFAULT 'active'
        );

        CREATE INDEX IF NOT EXISTS idx_sdk_sessions_claude_id ON sdk_sessions(content_session_id);
        CREATE INDEX IF NOT EXISTS idx_sdk_sessions_sdk_id ON sdk_sessions(memory_session_id);
        CREATE INDEX IF NOT EXISTS idx_sdk_sessions_project ON sdk_sessions(project);
        CREATE INDEX IF NOT EXISTS idx_sdk_sessions_status ON sdk_sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sdk_sessions_started ON sdk_sessions(started_at_epoch DESC);

        CREATE TABLE IF NOT EXISTS observations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          memory_session_id TEXT NOT NULL,
          project TEXT NOT NULL,
          text TEXT NOT NULL,
          type TEXT NOT NULL,
          created_at TEXT NOT NULL,
          created_at_epoch INTEGER NOT NULL,
          FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_observations_sdk_session ON observations(memory_session_id);
        CREATE INDEX IF NOT EXISTS idx_observations_project ON observations(project);
        CREATE INDEX IF NOT EXISTS idx_observations_type ON observations(type);
        CREATE INDEX IF NOT EXISTS idx_observations_created ON observations(created_at_epoch DESC);

        CREATE TABLE IF NOT EXISTS session_summaries (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          memory_session_id TEXT UNIQUE NOT NULL,
          project TEXT NOT NULL,
          request TEXT,
          investigated TEXT,
          learned TEXT,
          completed TEXT,
          next_steps TEXT,
          files_read TEXT,
          files_edited TEXT,
          notes TEXT,
          created_at TEXT NOT NULL,
          created_at_epoch INTEGER NOT NULL,
          FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_session_summaries_sdk_session ON session_summaries(memory_session_id);
        CREATE INDEX IF NOT EXISTS idx_session_summaries_project ON session_summaries(project);
        CREATE INDEX IF NOT EXISTS idx_session_summaries_created ON session_summaries(created_at_epoch DESC);
      `),this.db.prepare("INSERT INTO schema_versions (version, applied_at) VALUES (?, ?)").run(4,new Date().toISOString()),u.info("DB","Migration004 applied successfully"))}ensureWorkerPortColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(5))return;this.db.query("PRAGMA table_info(sdk_sessions)").all().some(n=>n.name==="worker_port")||(this.db.run("ALTER TABLE sdk_sessions ADD COLUMN worker_port INTEGER"),u.debug("DB","Added worker_port column to sdk_sessions table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(5,new Date().toISOString())}ensurePromptTrackingColumns(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(6))return;this.db.query("PRAGMA table_info(sdk_sessions)").all().some(a=>a.name==="prompt_counter")||(this.db.run("ALTER TABLE sdk_sessions ADD COLUMN prompt_counter INTEGER DEFAULT 0"),u.debug("DB","Added prompt_counter column to sdk_sessions table")),this.db.query("PRAGMA table_info(observations)").all().some(a=>a.name==="prompt_number")||(this.db.run("ALTER TABLE observations ADD COLUMN prompt_number INTEGER"),u.debug("DB","Added prompt_number column to observations table")),this.db.query("PRAGMA table_info(session_summaries)").all().some(a=>a.name==="prompt_number")||(this.db.run("ALTER TABLE session_summaries ADD COLUMN prompt_number INTEGER"),u.debug("DB","Added prompt_number column to session_summaries table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(6,new Date().toISOString())}removeSessionSummariesUniqueConstraint(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(7))return;if(!this.db.query("PRAGMA index_list(session_summaries)").all().some(n=>n.unique===1)){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(7,new Date().toISOString());return}u.debug("DB","Removing UNIQUE constraint from session_summaries.memory_session_id"),this.db.run("PRAGMA foreign_keys = OFF"),this.db.run("BEGIN TRANSACTION"),this.db.run(`
      CREATE TABLE session_summaries_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_session_id TEXT NOT NULL,
        project TEXT NOT NULL,
        request TEXT,
        investigated TEXT,
        learned TEXT,
        completed TEXT,
        next_steps TEXT,
        files_read TEXT,
        files_edited TEXT,
        notes TEXT,
        prompt_number INTEGER,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `),this.db.run(`
      INSERT INTO session_summaries_new
      SELECT id, memory_session_id, project, request, investigated, learned,
             completed, next_steps, files_read, files_edited, notes,
             prompt_number, created_at, created_at_epoch
      FROM session_summaries
    `),this.db.run("DROP TABLE session_summaries"),this.db.run("ALTER TABLE session_summaries_new RENAME TO session_summaries"),this.db.run(`
      CREATE INDEX idx_session_summaries_sdk_session ON session_summaries(memory_session_id);
      CREATE INDEX idx_session_summaries_project ON session_summaries(project);
      CREATE INDEX idx_session_summaries_created ON session_summaries(created_at_epoch DESC);
    `),this.db.run("COMMIT"),this.db.run("PRAGMA foreign_keys = ON"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(7,new Date().toISOString()),u.debug("DB","Successfully removed UNIQUE constraint from session_summaries.memory_session_id")}addObservationHierarchicalFields(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(8))return;if(this.db.query("PRAGMA table_info(observations)").all().some(n=>n.name==="title")){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(8,new Date().toISOString());return}u.debug("DB","Adding hierarchical fields to observations table"),this.db.run(`
      ALTER TABLE observations ADD COLUMN title TEXT;
      ALTER TABLE observations ADD COLUMN subtitle TEXT;
      ALTER TABLE observations ADD COLUMN facts TEXT;
      ALTER TABLE observations ADD COLUMN narrative TEXT;
      ALTER TABLE observations ADD COLUMN concepts TEXT;
      ALTER TABLE observations ADD COLUMN files_read TEXT;
      ALTER TABLE observations ADD COLUMN files_modified TEXT;
    `),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(8,new Date().toISOString()),u.debug("DB","Successfully added hierarchical fields to observations table")}makeObservationsTextNullable(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(9))return;let s=this.db.query("PRAGMA table_info(observations)").all().find(n=>n.name==="text");if(!s||s.notnull===0){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(9,new Date().toISOString());return}u.debug("DB","Making observations.text nullable"),this.db.run("PRAGMA foreign_keys = OFF"),this.db.run("BEGIN TRANSACTION"),this.db.run(`
      CREATE TABLE observations_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        memory_session_id TEXT NOT NULL,
        project TEXT NOT NULL,
        text TEXT,
        type TEXT NOT NULL,
        title TEXT,
        subtitle TEXT,
        facts TEXT,
        narrative TEXT,
        concepts TEXT,
        files_read TEXT,
        files_modified TEXT,
        prompt_number INTEGER,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(memory_session_id) REFERENCES sdk_sessions(memory_session_id) ON DELETE CASCADE
      )
    `),this.db.run(`
      INSERT INTO observations_new
      SELECT id, memory_session_id, project, text, type, title, subtitle, facts,
             narrative, concepts, files_read, files_modified, prompt_number,
             created_at, created_at_epoch
      FROM observations
    `),this.db.run("DROP TABLE observations"),this.db.run("ALTER TABLE observations_new RENAME TO observations"),this.db.run(`
      CREATE INDEX idx_observations_sdk_session ON observations(memory_session_id);
      CREATE INDEX idx_observations_project ON observations(project);
      CREATE INDEX idx_observations_type ON observations(type);
      CREATE INDEX idx_observations_created ON observations(created_at_epoch DESC);
    `),this.db.run("COMMIT"),this.db.run("PRAGMA foreign_keys = ON"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(9,new Date().toISOString()),u.debug("DB","Successfully made observations.text nullable")}createUserPromptsTable(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(10))return;if(this.db.query("PRAGMA table_info(user_prompts)").all().length>0){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(10,new Date().toISOString());return}u.debug("DB","Creating user_prompts table with FTS5 support"),this.db.run("BEGIN TRANSACTION"),this.db.run(`
      CREATE TABLE user_prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_session_id TEXT NOT NULL,
        prompt_number INTEGER NOT NULL,
        prompt_text TEXT NOT NULL,
        created_at TEXT NOT NULL,
        created_at_epoch INTEGER NOT NULL,
        FOREIGN KEY(content_session_id) REFERENCES sdk_sessions(content_session_id) ON DELETE CASCADE
      );

      CREATE INDEX idx_user_prompts_claude_session ON user_prompts(content_session_id);
      CREATE INDEX idx_user_prompts_created ON user_prompts(created_at_epoch DESC);
      CREATE INDEX idx_user_prompts_prompt_number ON user_prompts(prompt_number);
      CREATE INDEX idx_user_prompts_lookup ON user_prompts(content_session_id, prompt_number);
    `),this.db.run(`
      CREATE VIRTUAL TABLE user_prompts_fts USING fts5(
        prompt_text,
        content='user_prompts',
        content_rowid='id'
      );
    `),this.db.run(`
      CREATE TRIGGER user_prompts_ai AFTER INSERT ON user_prompts BEGIN
        INSERT INTO user_prompts_fts(rowid, prompt_text)
        VALUES (new.id, new.prompt_text);
      END;

      CREATE TRIGGER user_prompts_ad AFTER DELETE ON user_prompts BEGIN
        INSERT INTO user_prompts_fts(user_prompts_fts, rowid, prompt_text)
        VALUES('delete', old.id, old.prompt_text);
      END;

      CREATE TRIGGER user_prompts_au AFTER UPDATE ON user_prompts BEGIN
        INSERT INTO user_prompts_fts(user_prompts_fts, rowid, prompt_text)
        VALUES('delete', old.id, old.prompt_text);
        INSERT INTO user_prompts_fts(rowid, prompt_text)
        VALUES (new.id, new.prompt_text);
      END;
    `),this.db.run("COMMIT"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(10,new Date().toISOString()),u.debug("DB","Successfully created user_prompts table with FTS5 support")}ensureDiscoveryTokensColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(11))return;this.db.query("PRAGMA table_info(observations)").all().some(i=>i.name==="discovery_tokens")||(this.db.run("ALTER TABLE observations ADD COLUMN discovery_tokens INTEGER DEFAULT 0"),u.debug("DB","Added discovery_tokens column to observations table")),this.db.query("PRAGMA table_info(session_summaries)").all().some(i=>i.name==="discovery_tokens")||(this.db.run("ALTER TABLE session_summaries ADD COLUMN discovery_tokens INTEGER DEFAULT 0"),u.debug("DB","Added discovery_tokens column to session_summaries table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(11,new Date().toISOString())}createPendingMessagesTable(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(16))return;if(this.db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_messages'").all().length>0){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(16,new Date().toISOString());return}u.debug("DB","Creating pending_messages table"),this.db.run(`
      CREATE TABLE pending_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_db_id INTEGER NOT NULL,
        content_session_id TEXT NOT NULL,
        message_type TEXT NOT NULL CHECK(message_type IN ('observation', 'summarize')),
        tool_name TEXT,
        tool_input TEXT,
        tool_response TEXT,
        cwd TEXT,
        last_user_message TEXT,
        last_assistant_message TEXT,
        prompt_number INTEGER,
        status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'processed', 'failed')),
        retry_count INTEGER NOT NULL DEFAULT 0,
        created_at_epoch INTEGER NOT NULL,
        started_processing_at_epoch INTEGER,
        completed_at_epoch INTEGER,
        FOREIGN KEY (session_db_id) REFERENCES sdk_sessions(id) ON DELETE CASCADE
      )
    `),this.db.run("CREATE INDEX IF NOT EXISTS idx_pending_messages_session ON pending_messages(session_db_id)"),this.db.run("CREATE INDEX IF NOT EXISTS idx_pending_messages_status ON pending_messages(status)"),this.db.run("CREATE INDEX IF NOT EXISTS idx_pending_messages_claude_session ON pending_messages(content_session_id)"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(16,new Date().toISOString()),u.debug("DB","pending_messages table created successfully")}renameSessionIdColumns(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(17))return;u.debug("DB","Checking session ID columns for semantic clarity rename");let t=0,s=(n,o,i)=>{let d=this.db.query(`PRAGMA table_info(${n})`).all(),a=d.some(l=>l.name===o);return d.some(l=>l.name===i)?!1:a?(this.db.run(`ALTER TABLE ${n} RENAME COLUMN ${o} TO ${i}`),u.debug("DB",`Renamed ${n}.${o} to ${i}`),!0):(u.warn("DB",`Column ${o} not found in ${n}, skipping rename`),!1)};s("sdk_sessions","claude_session_id","content_session_id")&&t++,s("sdk_sessions","sdk_session_id","memory_session_id")&&t++,s("pending_messages","claude_session_id","content_session_id")&&t++,s("observations","sdk_session_id","memory_session_id")&&t++,s("session_summaries","sdk_session_id","memory_session_id")&&t++,s("user_prompts","claude_session_id","content_session_id")&&t++,this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(17,new Date().toISOString()),t>0?u.debug("DB",`Successfully renamed ${t} session ID columns`):u.debug("DB","No session ID column renames needed (already up to date)")}repairSessionIdColumnRename(){this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(19)||this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(19,new Date().toISOString())}addFailedAtEpochColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(20))return;this.db.query("PRAGMA table_info(pending_messages)").all().some(n=>n.name==="failed_at_epoch")||(this.db.run("ALTER TABLE pending_messages ADD COLUMN failed_at_epoch INTEGER"),u.debug("DB","Added failed_at_epoch column to pending_messages table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(20,new Date().toISOString())}ensureSessionPlansTable(){this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(21)||(this.db.run(`
      CREATE TABLE IF NOT EXISTS session_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_db_id INTEGER NOT NULL UNIQUE,
        plan_path TEXT NOT NULL,
        plan_status TEXT DEFAULT 'PENDING',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_db_id) REFERENCES sdk_sessions(id) ON DELETE CASCADE
      )
    `),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(21,new Date().toISOString()))}createProjectRootsTable(){this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(23)||(this.db.run(`
      CREATE TABLE IF NOT EXISTS project_roots (
        project TEXT PRIMARY KEY,
        root_path TEXT NOT NULL,
        last_seen_at TEXT NOT NULL DEFAULT (datetime('now'))
      )
    `),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(23,new Date().toISOString()))}ensureNotificationsTable(){this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(24)||(this.db.run(`
      CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        plan_path TEXT,
        session_id TEXT,
        is_read INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
      )
    `),this.db.run("CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(is_read, created_at DESC)"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(24,new Date().toISOString()))}upsertProjectRoot(e,t){this.db.prepare(`INSERT INTO project_roots (project, root_path, last_seen_at)
         VALUES (?, ?, datetime('now'))
         ON CONFLICT(project) DO UPDATE SET root_path = excluded.root_path, last_seen_at = datetime('now')`).run(e,t)}getProjectRoot(e){return this.db.prepare("SELECT root_path FROM project_roots WHERE project = ?").get(e)?.root_path??null}getAllProjectRoots(){return this.db.prepare("SELECT project, root_path, last_seen_at FROM project_roots ORDER BY project").all().map(t=>({project:t.project,rootPath:t.root_path,lastSeenAt:t.last_seen_at}))}updateMemorySessionId(e,t){this.db.prepare(`
      UPDATE sdk_sessions
      SET memory_session_id = ?
      WHERE id = ?
    `).run(t,e)}getRecentSummaries(e,t=10){return this.db.prepare(`
      SELECT
        request, investigated, learned, completed, next_steps,
        files_read, files_edited, notes, prompt_number, created_at
      FROM session_summaries
      WHERE project = ?
      ORDER BY created_at_epoch DESC
      LIMIT ?
    `).all(e,t)}getRecentSummariesWithSessionInfo(e,t=3){return this.db.prepare(`
      SELECT
        memory_session_id, request, learned, completed, next_steps,
        prompt_number, created_at
      FROM session_summaries
      WHERE project = ?
      ORDER BY created_at_epoch DESC
      LIMIT ?
    `).all(e,t)}getRecentObservations(e,t=20){return this.db.prepare(`
      SELECT type, text, prompt_number, created_at
      FROM observations
      WHERE project = ?
      ORDER BY created_at_epoch DESC
      LIMIT ?
    `).all(e,t)}getAllRecentObservations(e=100){return this.db.prepare(`
      SELECT id, type, title, subtitle, text, project, prompt_number, created_at, created_at_epoch
      FROM observations
      ORDER BY created_at_epoch DESC
      LIMIT ?
    `).all(e)}getAllRecentSummaries(e=50){return this.db.prepare(`
      SELECT id, request, investigated, learned, completed, next_steps,
             files_read, files_edited, notes, project, prompt_number,
             created_at, created_at_epoch
      FROM session_summaries
      ORDER BY created_at_epoch DESC
      LIMIT ?
    `).all(e)}getAllRecentUserPrompts(e=100){return this.db.prepare(`
      SELECT
        up.id,
        up.content_session_id,
        s.project,
        up.prompt_number,
        up.prompt_text,
        up.created_at,
        up.created_at_epoch
      FROM user_prompts up
      LEFT JOIN sdk_sessions s ON up.content_session_id = s.content_session_id
      ORDER BY up.created_at_epoch DESC
      LIMIT ?
    `).all(e)}getAllProjects(){return this.db.prepare(`
      SELECT DISTINCT project
      FROM sdk_sessions
      WHERE project IS NOT NULL AND project != ''
      ORDER BY project ASC
    `).all().map(s=>s.project)}getLatestUserPrompt(e){return this.db.prepare(`
      SELECT
        up.*,
        s.memory_session_id,
        s.project
      FROM user_prompts up
      JOIN sdk_sessions s ON up.content_session_id = s.content_session_id
      WHERE up.content_session_id = ?
      ORDER BY up.created_at_epoch DESC
      LIMIT 1
    `).get(e)}getRecentSessionsWithStatus(e,t=3){return this.db.prepare(`
      SELECT * FROM (
        SELECT
          s.memory_session_id,
          s.status,
          s.started_at,
          s.started_at_epoch,
          s.user_prompt,
          CASE WHEN sum.memory_session_id IS NOT NULL THEN 1 ELSE 0 END as has_summary
        FROM sdk_sessions s
        LEFT JOIN session_summaries sum ON s.memory_session_id = sum.memory_session_id
        WHERE s.project = ? AND s.memory_session_id IS NOT NULL
        GROUP BY s.memory_session_id
        ORDER BY s.started_at_epoch DESC
        LIMIT ?
      )
      ORDER BY started_at_epoch ASC
    `).all(e,t)}getObservationsForSession(e){return this.db.prepare(`
      SELECT title, subtitle, type, prompt_number
      FROM observations
      WHERE memory_session_id = ?
      ORDER BY created_at_epoch ASC
    `).all(e)}getObservationById(e){return this.db.prepare(`
      SELECT *
      FROM observations
      WHERE id = ?
    `).get(e)||null}getObservationsByIds(e,t={}){if(e.length===0)return[];let{orderBy:s="date_desc",limit:n,project:o,type:i,concepts:d,files:a}=t,c=s==="date_asc"?"ASC":"DESC",l=n?`LIMIT ${n}`:"",m=e.map(()=>"?").join(","),g=[...e],E=[];if(o&&(E.push("project = ?"),g.push(o)),i)if(Array.isArray(i)){let _=i.map(()=>"?").join(",");E.push(`type IN (${_})`),g.push(...i)}else E.push("type = ?"),g.push(i);if(d){let _=Array.isArray(d)?d:[d],f=_.map(()=>"EXISTS (SELECT 1 FROM json_each(concepts) WHERE value = ?)");g.push(..._),E.push(`(${f.join(" OR ")})`)}if(a){let _=Array.isArray(a)?a:[a],f=_.map(()=>"(EXISTS (SELECT 1 FROM json_each(files_read) WHERE value LIKE ?) OR EXISTS (SELECT 1 FROM json_each(files_modified) WHERE value LIKE ?))");_.forEach(h=>{g.push(`%${h}%`,`%${h}%`)}),E.push(`(${f.join(" OR ")})`)}let T=E.length>0?`WHERE id IN (${m}) AND ${E.join(" AND ")}`:`WHERE id IN (${m})`;return this.db.prepare(`
      SELECT *
      FROM observations
      ${T}
      ORDER BY created_at_epoch ${c}
      ${l}
    `).all(...g)}deleteProjectData(e){let t=this.db.prepare("SELECT COUNT(*) as count FROM observations WHERE project = ?").get(e).count;return this.db.prepare("DELETE FROM sdk_sessions WHERE project = ?").run(e),this.db.prepare("DELETE FROM observations WHERE project = ?").run(e),t}deleteObservation(e){return this.db.prepare("DELETE FROM observations WHERE id = ?").run(e).changes>0}deleteObservations(e){if(e.length===0)return 0;let t=e.map(()=>"?").join(",");return this.db.prepare(`DELETE FROM observations WHERE id IN (${t})`).run(...e).changes}getSummaryForSession(e){return this.db.prepare(`
      SELECT
        request, investigated, learned, completed, next_steps,
        files_read, files_edited, notes, prompt_number, created_at,
        created_at_epoch
      FROM session_summaries
      WHERE memory_session_id = ?
      ORDER BY created_at_epoch DESC
      LIMIT 1
    `).get(e)||null}getFilesForSession(e){let s=this.db.prepare(`
      SELECT files_read, files_modified
      FROM observations
      WHERE memory_session_id = ?
    `).all(e),n=new Set,o=new Set;for(let i of s){if(i.files_read){let d=JSON.parse(i.files_read);Array.isArray(d)&&d.forEach(a=>n.add(a))}if(i.files_modified){let d=JSON.parse(i.files_modified);Array.isArray(d)&&d.forEach(a=>o.add(a))}}return{filesRead:Array.from(n),filesModified:Array.from(o)}}getSessionById(e){return this.db.prepare(`
      SELECT id, content_session_id, memory_session_id, project, user_prompt
      FROM sdk_sessions
      WHERE id = ?
      LIMIT 1
    `).get(e)||null}getSessionByContentId(e){return this.db.prepare(`
      SELECT id, content_session_id, memory_session_id, project, user_prompt
      FROM sdk_sessions
      WHERE content_session_id = ?
      LIMIT 1
    `).get(e)||null}getSdkSessionsBySessionIds(e){if(e.length===0)return[];let t=e.map(()=>"?").join(",");return this.db.prepare(`
      SELECT id, content_session_id, memory_session_id, project, user_prompt,
             started_at, started_at_epoch, completed_at, completed_at_epoch, status
      FROM sdk_sessions
      WHERE memory_session_id IN (${t})
      ORDER BY started_at_epoch DESC
    `).all(...e)}markSessionCompleted(e){let t=new Date,s=t.getTime();this.db.prepare(`
      UPDATE sdk_sessions
      SET status = 'completed',
          completed_at = ?,
          completed_at_epoch = ?
      WHERE id = ? AND status = 'active'
    `).run(t.toISOString(),s,e)}getPromptNumberFromUserPrompts(e){return this.db.prepare(`
      SELECT COUNT(*) as count FROM user_prompts WHERE content_session_id = ?
    `).get(e).count}createSDKSession(e,t,s){let n=new Date,o=n.getTime(),i=crypto.randomUUID();return this.db.prepare(`
      INSERT OR IGNORE INTO sdk_sessions
      (content_session_id, memory_session_id, project, user_prompt, started_at, started_at_epoch, status)
      VALUES (?, ?, ?, ?, ?, ?, 'active')
    `).run(e,i,t,s,n.toISOString(),o),this.db.prepare(`
      UPDATE sdk_sessions
      SET status = 'active', completed_at = NULL, completed_at_epoch = NULL
      WHERE content_session_id = ? AND status != 'active'
    `).run(e),this.db.prepare("SELECT id FROM sdk_sessions WHERE content_session_id = ?").get(e).id}saveUserPrompt(e,t,s){let n=new Date,o=n.getTime();return this.db.prepare(`
      INSERT INTO user_prompts
      (content_session_id, prompt_number, prompt_text, created_at, created_at_epoch)
      VALUES (?, ?, ?, ?, ?)
    `).run(e,t,s,n.toISOString(),o).lastInsertRowid}getUserPrompt(e,t){return this.db.prepare(`
      SELECT prompt_text
      FROM user_prompts
      WHERE content_session_id = ? AND prompt_number = ?
      LIMIT 1
    `).get(e,t)?.prompt_text??null}storeObservation(e,t,s,n,o=0,i){let d=i??Date.now(),a=new Date(d).toISOString(),l=this.db.prepare(`
      INSERT INTO observations
      (memory_session_id, project, type, title, subtitle, facts, narrative, concepts,
       files_read, files_modified, prompt_number, discovery_tokens, created_at, created_at_epoch)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(e,t,s.type,s.title,s.subtitle,JSON.stringify(s.facts),s.narrative,JSON.stringify(s.concepts),JSON.stringify(s.files_read),JSON.stringify(s.files_modified),n||null,o,a,d);return{id:Number(l.lastInsertRowid),createdAtEpoch:d}}storeSummary(e,t,s,n,o=0,i){let d=i??Date.now(),a=new Date(d).toISOString(),l=this.db.prepare(`
      INSERT INTO session_summaries
      (memory_session_id, project, request, investigated, learned, completed,
       next_steps, notes, prompt_number, discovery_tokens, created_at, created_at_epoch)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(e,t,s.request,s.investigated,s.learned,s.completed,s.next_steps,s.notes,n||null,o,a,d);return{id:Number(l.lastInsertRowid),createdAtEpoch:d}}storeObservations(e,t,s,n,o,i=0,d){let a=d??Date.now(),c=new Date(a).toISOString();return this.db.transaction(()=>{let m=[],g=this.db.prepare(`
        INSERT INTO observations
        (memory_session_id, project, type, title, subtitle, facts, narrative, concepts,
         files_read, files_modified, prompt_number, discovery_tokens, created_at, created_at_epoch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);for(let T of s){let O=g.run(e,t,T.type,T.title,T.subtitle,JSON.stringify(T.facts),T.narrative,JSON.stringify(T.concepts),JSON.stringify(T.files_read),JSON.stringify(T.files_modified),o||null,i,c,a);m.push(Number(O.lastInsertRowid))}let E=null;if(n){let O=this.db.prepare(`
          INSERT INTO session_summaries
          (memory_session_id, project, request, investigated, learned, completed,
           next_steps, notes, prompt_number, discovery_tokens, created_at, created_at_epoch)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(e,t,n.request,n.investigated,n.learned,n.completed,n.next_steps,n.notes,o||null,i,c,a);E=Number(O.lastInsertRowid)}return{observationIds:m,summaryId:E,createdAtEpoch:a}})()}storeObservationsAndMarkComplete(e,t,s,n,o,i,d,a=0,c){let l=c??Date.now(),m=new Date(l).toISOString();return this.db.transaction(()=>{let E=[],T=this.db.prepare(`
        INSERT INTO observations
        (memory_session_id, project, type, title, subtitle, facts, narrative, concepts,
         files_read, files_modified, prompt_number, discovery_tokens, created_at, created_at_epoch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);for(let f of s){let h=T.run(e,t,f.type,f.title,f.subtitle,JSON.stringify(f.facts),f.narrative,JSON.stringify(f.concepts),JSON.stringify(f.files_read),JSON.stringify(f.files_modified),d||null,a,m,l);E.push(Number(h.lastInsertRowid))}let O;if(n){let h=this.db.prepare(`
          INSERT INTO session_summaries
          (memory_session_id, project, request, investigated, learned, completed,
           next_steps, notes, prompt_number, discovery_tokens, created_at, created_at_epoch)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(e,t,n.request,n.investigated,n.learned,n.completed,n.next_steps,n.notes,d||null,a,m,l);O=Number(h.lastInsertRowid)}return this.db.prepare(`
        UPDATE pending_messages
        SET
          status = 'processed',
          completed_at_epoch = ?,
          tool_input = NULL,
          tool_response = NULL
        WHERE id = ? AND status = 'processing'
      `).run(l,o),{observationIds:E,summaryId:O,createdAtEpoch:l}})()}getSessionSummariesByIds(e,t={}){if(e.length===0)return[];let{orderBy:s="date_desc",limit:n,project:o}=t,i=s==="date_asc"?"ASC":"DESC",d=n?`LIMIT ${n}`:"",a=e.map(()=>"?").join(","),c=[...e],l=o?`WHERE id IN (${a}) AND project = ?`:`WHERE id IN (${a})`;return o&&c.push(o),this.db.prepare(`
      SELECT * FROM session_summaries
      ${l}
      ORDER BY created_at_epoch ${i}
      ${d}
    `).all(...c)}getUserPromptsByIds(e,t={}){if(e.length===0)return[];let{orderBy:s="date_desc",limit:n,project:o}=t,i=s==="date_asc"?"ASC":"DESC",d=n?`LIMIT ${n}`:"",a=e.map(()=>"?").join(","),c=[...e],l=o?"AND s.project = ?":"";return o&&c.push(o),this.db.prepare(`
      SELECT
        up.*,
        s.project,
        s.memory_session_id
      FROM user_prompts up
      JOIN sdk_sessions s ON up.content_session_id = s.content_session_id
      WHERE up.id IN (${a}) ${l}
      ORDER BY up.created_at_epoch ${i}
      ${d}
    `).all(...c)}getTimelineAroundTimestamp(e,t=10,s=10,n){return this.getTimelineAroundObservation(null,e,t,s,n)}getTimelineAroundObservation(e,t,s=10,n=10,o){let i=o?"AND project = ?":"",d=o?[o]:[],a,c;if(e!==null){let _=`
        SELECT id, created_at_epoch
        FROM observations
        WHERE id <= ? ${i}
        ORDER BY id DESC
        LIMIT ?
      `,f=`
        SELECT id, created_at_epoch
        FROM observations
        WHERE id >= ? ${i}
        ORDER BY id ASC
        LIMIT ?
      `;try{let h=this.db.prepare(_).all(e,...d,s+1),I=this.db.prepare(f).all(e,...d,n+1);if(h.length===0&&I.length===0)return{observations:[],sessions:[],prompts:[]};a=h.length>0?h[h.length-1].created_at_epoch:t,c=I.length>0?I[I.length-1].created_at_epoch:t}catch(h){return u.error("DB","Error getting boundary observations",void 0,{error:h,project:o}),{observations:[],sessions:[],prompts:[]}}}else{let _=`
        SELECT created_at_epoch
        FROM observations
        WHERE created_at_epoch <= ? ${i}
        ORDER BY created_at_epoch DESC
        LIMIT ?
      `,f=`
        SELECT created_at_epoch
        FROM observations
        WHERE created_at_epoch >= ? ${i}
        ORDER BY created_at_epoch ASC
        LIMIT ?
      `;try{let h=this.db.prepare(_).all(t,...d,s),I=this.db.prepare(f).all(t,...d,n+1);if(h.length===0&&I.length===0)return{observations:[],sessions:[],prompts:[]};a=h.length>0?h[h.length-1].created_at_epoch:t,c=I.length>0?I[I.length-1].created_at_epoch:t}catch(h){return u.error("DB","Error getting boundary timestamps",void 0,{error:h,project:o}),{observations:[],sessions:[],prompts:[]}}}let l=`
      SELECT *
      FROM observations
      WHERE created_at_epoch >= ? AND created_at_epoch <= ? ${i}
      ORDER BY created_at_epoch ASC
    `,m=`
      SELECT *
      FROM session_summaries
      WHERE created_at_epoch >= ? AND created_at_epoch <= ? ${i}
      ORDER BY created_at_epoch ASC
    `,g=`
      SELECT up.*, s.project, s.memory_session_id
      FROM user_prompts up
      JOIN sdk_sessions s ON up.content_session_id = s.content_session_id
      WHERE up.created_at_epoch >= ? AND up.created_at_epoch <= ? ${i.replace("project","s.project")}
      ORDER BY up.created_at_epoch ASC
    `,E=this.db.prepare(l).all(a,c,...d),T=this.db.prepare(m).all(a,c,...d),O=this.db.prepare(g).all(a,c,...d);return{observations:E,sessions:T.map(_=>({id:_.id,memory_session_id:_.memory_session_id,project:_.project,request:_.request,completed:_.completed,next_steps:_.next_steps,created_at:_.created_at,created_at_epoch:_.created_at_epoch})),prompts:O.map(_=>({id:_.id,content_session_id:_.content_session_id,prompt_number:_.prompt_number,prompt_text:_.prompt_text,project:_.project,created_at:_.created_at,created_at_epoch:_.created_at_epoch}))}}getPromptById(e){return this.db.prepare(`
      SELECT
        p.id,
        p.content_session_id,
        p.prompt_number,
        p.prompt_text,
        s.project,
        p.created_at,
        p.created_at_epoch
      FROM user_prompts p
      LEFT JOIN sdk_sessions s ON p.content_session_id = s.content_session_id
      WHERE p.id = ?
      LIMIT 1
    `).get(e)||null}getPromptsByIds(e){if(e.length===0)return[];let t=e.map(()=>"?").join(",");return this.db.prepare(`
      SELECT
        p.id,
        p.content_session_id,
        p.prompt_number,
        p.prompt_text,
        s.project,
        p.created_at,
        p.created_at_epoch
      FROM user_prompts p
      LEFT JOIN sdk_sessions s ON p.content_session_id = s.content_session_id
      WHERE p.id IN (${t})
      ORDER BY p.created_at_epoch DESC
    `).all(...e)}getSessionSummaryById(e){return this.db.prepare(`
      SELECT
        id,
        memory_session_id,
        content_session_id,
        project,
        user_prompt,
        request_summary,
        learned_summary,
        status,
        created_at,
        created_at_epoch
      FROM sdk_sessions
      WHERE id = ?
      LIMIT 1
    `).get(e)||null}getOrCreateManualSession(e){let t=`manual-${e}`,s=`manual-content-${e}`;if(this.db.prepare("SELECT memory_session_id FROM sdk_sessions WHERE memory_session_id = ?").get(t))return t;let o=new Date;return this.db.prepare(`
      INSERT INTO sdk_sessions (memory_session_id, content_session_id, project, started_at, started_at_epoch, status)
      VALUES (?, ?, ?, ?, ?, 'active')
    `).run(t,s,e,o.toISOString(),o.getTime()),u.info("SESSION","Created manual session",{memorySessionId:t,project:e}),t}close(){this.db.close()}importSdkSession(e){let t=this.db.prepare("SELECT id FROM sdk_sessions WHERE content_session_id = ?").get(e.content_session_id);return t?{imported:!1,id:t.id}:{imported:!0,id:this.db.prepare(`
      INSERT INTO sdk_sessions (
        content_session_id, memory_session_id, project, user_prompt,
        started_at, started_at_epoch, completed_at, completed_at_epoch, status
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(e.content_session_id,e.memory_session_id,e.project,e.user_prompt,e.started_at,e.started_at_epoch,e.completed_at,e.completed_at_epoch,e.status).lastInsertRowid}}importSessionSummary(e){let t=this.db.prepare("SELECT id FROM session_summaries WHERE memory_session_id = ?").get(e.memory_session_id);return t?{imported:!1,id:t.id}:{imported:!0,id:this.db.prepare(`
      INSERT INTO session_summaries (
        memory_session_id, project, request, investigated, learned,
        completed, next_steps, files_read, files_edited, notes,
        prompt_number, discovery_tokens, created_at, created_at_epoch
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(e.memory_session_id,e.project,e.request,e.investigated,e.learned,e.completed,e.next_steps,e.files_read,e.files_edited,e.notes,e.prompt_number,e.discovery_tokens||0,e.created_at,e.created_at_epoch).lastInsertRowid}}importObservation(e){let t=this.db.prepare(`
      SELECT id FROM observations
      WHERE memory_session_id = ? AND title = ? AND created_at_epoch = ?
    `).get(e.memory_session_id,e.title,e.created_at_epoch);return t?{imported:!1,id:t.id}:{imported:!0,id:this.db.prepare(`
      INSERT INTO observations (
        memory_session_id, project, text, type, title, subtitle,
        facts, narrative, concepts, files_read, files_modified,
        prompt_number, discovery_tokens, created_at, created_at_epoch
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(e.memory_session_id,e.project,e.text,e.type,e.title,e.subtitle,e.facts,e.narrative,e.concepts,e.files_read,e.files_modified,e.prompt_number,e.discovery_tokens||0,e.created_at,e.created_at_epoch).lastInsertRowid}}importUserPrompt(e){let t=this.db.prepare(`
      SELECT id FROM user_prompts
      WHERE content_session_id = ? AND prompt_number = ?
    `).get(e.content_session_id,e.prompt_number);return t?{imported:!1,id:t.id}:{imported:!0,id:this.db.prepare(`
      INSERT INTO user_prompts (
        content_session_id, prompt_number, prompt_text,
        created_at, created_at_epoch
      ) VALUES (?, ?, ?, ?, ?)
    `).run(e.content_session_id,e.prompt_number,e.prompt_text,e.created_at,e.created_at_epoch).lastInsertRowid}}getAllTags(){return this.db.prepare(`
      SELECT * FROM tags
      ORDER BY usage_count DESC, name ASC
    `).all()}getOrCreateTag(e,t){let s=e.toLowerCase().trim(),n=this.db.prepare(`
      SELECT id, name, color FROM tags WHERE name = ?
    `).get(s);if(n)return{...n,created:!1};let o=new Date;return{id:this.db.prepare(`
      INSERT INTO tags (name, color, created_at, created_at_epoch)
      VALUES (?, ?, ?, ?)
    `).run(s,t||"#6b7280",o.toISOString(),o.getTime()).lastInsertRowid,name:s,color:t||"#6b7280",created:!0}}updateTag(e,t){let s=[],n=[];return t.name!==void 0&&(s.push("name = ?"),n.push(t.name.toLowerCase().trim())),t.color!==void 0&&(s.push("color = ?"),n.push(t.color)),t.description!==void 0&&(s.push("description = ?"),n.push(t.description)),s.length===0?!1:(n.push(e),this.db.prepare(`
      UPDATE tags SET ${s.join(", ")} WHERE id = ?
    `).run(...n).changes>0)}deleteTag(e){return this.db.prepare("DELETE FROM tags WHERE id = ?").run(e).changes>0}addTagsToObservation(e,t){let s=this.getObservationById(e);if(!s)return;let n=[];try{n=s.tags?JSON.parse(s.tags):[]}catch{n=[]}let o=t.map(a=>a.toLowerCase().trim()),i=[...new Set([...n,...o])];this.db.prepare("UPDATE observations SET tags = ? WHERE id = ?").run(JSON.stringify(i),e);for(let a of o)n.includes(a)||(this.getOrCreateTag(a),this.db.prepare("UPDATE tags SET usage_count = usage_count + 1 WHERE name = ?").run(a))}removeTagsFromObservation(e,t){let s=this.getObservationById(e);if(!s)return;let n=[];try{n=s.tags?JSON.parse(s.tags):[]}catch{n=[]}let o=t.map(a=>a.toLowerCase().trim()),i=n.filter(a=>!o.includes(a));this.db.prepare("UPDATE observations SET tags = ? WHERE id = ?").run(JSON.stringify(i),e);for(let a of o)n.includes(a)&&this.db.prepare("UPDATE tags SET usage_count = MAX(0, usage_count - 1) WHERE name = ?").run(a)}getObservationTags(e){let t=this.getObservationById(e);if(!t?.tags)return[];try{return JSON.parse(t.tags)}catch{return[]}}getObservationsByTags(e,t={}){let{matchAll:s=!1,limit:n=50,project:o}=t,i=e.map(l=>l.toLowerCase().trim()),d,a=[];return s?(d=`SELECT * FROM observations WHERE tags IS NOT NULL AND ${i.map(()=>"EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)").join(" AND ")}`,a.push(...i)):(d=`SELECT * FROM observations WHERE tags IS NOT NULL AND (${i.map(()=>"EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)").join(" OR ")})`,a.push(...i)),o&&(d+=" AND project = ?",a.push(o)),d+=" ORDER BY created_at_epoch DESC LIMIT ?",a.push(n),this.db.prepare(d).all(...a)}getPopularTags(e=20){return this.db.prepare(`
      SELECT name, color, usage_count FROM tags
      WHERE usage_count > 0
      ORDER BY usage_count DESC
      LIMIT ?
    `).all(e)}suggestTagsForObservation(e){let t=this.getObservationById(e);if(!t)return[];let s=[];if(t.concepts)try{let i=JSON.parse(t.concepts);s.push(...i)}catch{typeof t.concepts=="string"&&s.push(...t.concepts.split(",").map(i=>i.trim()))}t.type&&s.push(t.type);let n=this.getAllTags(),o=new Set(n.map(i=>i.name));return[...new Set(s.map(i=>i.toLowerCase().trim()))].filter(Boolean)}};var L=C(require("path"),1),V=C(require("fs"),1);function _e(r){if(!r||r.trim()==="")return u.warn("PROJECT_NAME","Empty cwd provided, using fallback",{cwd:r}),"unknown-project";let e=L.default.basename(r);if(e===""){if(process.platform==="win32"){let n=r.match(/^([A-Z]):\\/i);if(n){let i=`drive-${n[1].toUpperCase()}`;return u.info("PROJECT_NAME","Drive root detected",{cwd:r,projectName:i}),i}}return u.warn("PROJECT_NAME","Root directory detected, using fallback",{cwd:r}),"unknown-project"}let t=Lt(r);return t||e}function Lt(r){try{let e;try{e=V.default.statSync(r).isDirectory()?r:L.default.dirname(r)}catch{e=L.default.dirname(r)}let t=L.default.parse(e).root,s=0,n=20;for(;e!==t&&s<n;){let o=L.default.join(e,".git");try{if(V.default.existsSync(o))return L.default.basename(e)}catch{}e=L.default.dirname(e),s++}return null}catch{return null}}var Ee=C(require("path"),1),ge=require("os");function q(){let r=Ee.default.join((0,ge.homedir)(),".pilot/memory","settings.json"),e=A.loadFromFile(r),t=new Set(e.CLAUDE_PILOT_CONTEXT_OBSERVATION_TYPES.split(",").map(n=>n.trim()).filter(Boolean)),s=new Set(e.CLAUDE_PILOT_CONTEXT_OBSERVATION_CONCEPTS.split(",").map(n=>n.trim()).filter(Boolean));return{totalObservationCount:parseInt(e.CLAUDE_PILOT_CONTEXT_OBSERVATIONS,10),fullObservationCount:parseInt(e.CLAUDE_PILOT_CONTEXT_FULL_COUNT,10),sessionCount:parseInt(e.CLAUDE_PILOT_CONTEXT_SESSION_COUNT,10),showReadTokens:e.CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS,showWorkTokens:e.CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS,showSavingsAmount:e.CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT,showSavingsPercent:e.CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT,observationTypes:t,observationConcepts:s,fullObservationField:e.CLAUDE_PILOT_CONTEXT_FULL_FIELD,showLastSummary:e.CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY,showLastMessage:e.CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE}}var p={reset:"\x1B[0m",bright:"\x1B[1m",dim:"\x1B[2m",cyan:"\x1B[36m",green:"\x1B[32m",yellow:"\x1B[33m",blue:"\x1B[34m",magenta:"\x1B[35m",gray:"\x1B[90m",red:"\x1B[31m"},Te=4,x=1;var he={name:"Code Development",description:"Software development and engineering work",version:"1.0.0",observation_types:[{id:"bugfix",label:"Bug Fix",description:"Something was broken, now fixed",emoji:"\u{1F534}",work_emoji:"\u{1F6E0}\uFE0F"},{id:"feature",label:"Feature",description:"New capability or functionality added",emoji:"\u{1F7E3}",work_emoji:"\u{1F6E0}\uFE0F"},{id:"refactor",label:"Refactor",description:"Code restructured, behavior unchanged",emoji:"\u{1F504}",work_emoji:"\u{1F6E0}\uFE0F"},{id:"change",label:"Change",description:"Generic modification (docs, config, misc)",emoji:"\u2705",work_emoji:"\u{1F6E0}\uFE0F"},{id:"discovery",label:"Discovery",description:"Learning about existing system",emoji:"\u{1F535}",work_emoji:"\u{1F50D}"},{id:"decision",label:"Decision",description:"Architectural/design choice with rationale",emoji:"\u2696\uFE0F",work_emoji:"\u2696\uFE0F"}],observation_concepts:[{id:"how-it-works",label:"How It Works",description:"Understanding mechanisms"},{id:"why-it-exists",label:"Why It Exists",description:"Purpose or rationale"},{id:"what-changed",label:"What Changed",description:"Modifications made"},{id:"problem-solution",label:"Problem-Solution",description:"Issues and their fixes"},{id:"gotcha",label:"Gotcha",description:"Traps or edge cases"},{id:"pattern",label:"Pattern",description:"Reusable approach"},{id:"trade-off",label:"Trade-Off",description:"Pros/cons of a decision"}],prompts:{system_identity:`[MEMORY] You are a specialized observer tool for creating searchable memory FOR FUTURE SESSIONS.

CRITICAL: Record what was LEARNED/BUILT/FIXED/DEPLOYED/CONFIGURED, not what you (the observer) are doing.

You do not have access to tools. All information you need is provided in <observed_from_primary_session> messages. Create observations from what you observe - no investigation needed.`,spatial_awareness:`SPATIAL AWARENESS: Tool executions include the working directory (tool_cwd) to help you understand:
- Which repository/project is being worked on
- Where files are located relative to the project root
- How to match requested paths to actual execution paths`,observer_role:"Your job is to monitor a different Claude Code session happening RIGHT NOW, with the goal of creating observations and progress summaries as the work is being done LIVE by the user. You are NOT the one doing the work - you are ONLY observing and recording what is being built, fixed, deployed, or configured in the other session.",recording_focus:`WHAT TO RECORD
--------------
Focus on deliverables and capabilities:
- What the system NOW DOES differently (new capabilities)
- What shipped to users/production (features, fixes, configs, docs)
- Changes in technical domains (auth, data, UI, infra, DevOps, docs)

Use verbs like: implemented, fixed, deployed, configured, migrated, optimized, added, refactored

\u2705 GOOD EXAMPLES (describes what was built):
- "Authentication now supports OAuth2 with PKCE flow"
- "Deployment pipeline runs canary releases with auto-rollback"
- "Database indexes optimized for common query patterns"

\u274C BAD EXAMPLES (describes observation process - DO NOT DO THIS):
- "Analyzed authentication implementation and stored findings"
- "Tracked deployment steps and logged outcomes"
- "Monitored database performance and recorded metrics"`,skip_guidance:`WHEN TO SKIP
------------
Skip routine operations:
- Empty status checks
- Package installations with no errors
- Simple file listings
- Repetitive operations you've already documented
- If file related research comes back as empty or not found

IMPORTANT: If you decide to skip, output NOTHING AT ALL. Do not say 'no output needed' or explain why you're skipping. Simply produce zero output - an empty response.`,type_guidance:`**type**: MUST be EXACTLY one of these 6 options (no other values allowed):
      - bugfix: something was broken, now fixed
      - feature: new capability or functionality added
      - refactor: code restructured, behavior unchanged
      - change: generic modification (docs, config, misc)
      - discovery: learning about existing system
      - decision: architectural/design choice with rationale`,concept_guidance:`**concepts**: 2-5 knowledge-type categories. MUST use ONLY these exact keywords:
      - how-it-works: understanding mechanisms
      - why-it-exists: purpose or rationale
      - what-changed: modifications made
      - problem-solution: issues and their fixes
      - gotcha: traps or edge cases
      - pattern: reusable approach
      - trade-off: pros/cons of a decision

    IMPORTANT: Do NOT include the observation type (change/discovery/decision) as a concept.
    Types and concepts are separate dimensions.`,field_guidance:`**facts**: Concise, self-contained statements
Each fact is ONE piece of information
      No pronouns - each fact must stand alone
      Include specific details: filenames, functions, values

**files**: All files touched (full paths from project root)`,output_format_header:`OUTPUT FORMAT
-------------
Output observations using this XML structure:`,format_examples:"",footer:`IMPORTANT! DO NOT do any work right now other than generating this OBSERVATIONS from tool use messages - and remember that you are a memory agent designed to summarize a DIFFERENT claude code session, not this one.

Never reference yourself or your own actions. Do not output anything other than the observation content formatted in the XML structure above. All other output is ignored by the system, and the system has been designed to be smart about token usage. Please spend your tokens wisely on useful observations.

Remember that we record these observations as a way of helping us stay on track with our progress, and to help us keep important decisions and changes at the forefront of our minds! :) Thank you so much for your help!`,xml_title_placeholder:"[**title**: Short title capturing the core action or topic]",xml_subtitle_placeholder:"[**subtitle**: One sentence explanation (max 24 words)]",xml_fact_placeholder:"[Concise, self-contained statement]",xml_narrative_placeholder:"[**narrative**: Full context: What was done, how it works, why it matters]",xml_concept_placeholder:"[knowledge-type-category]",xml_file_placeholder:"[path/to/file]",xml_summary_request_placeholder:"[Short title capturing the user's request AND the substance of what was discussed/done]",xml_summary_investigated_placeholder:"[What has been explored so far? What was examined?]",xml_summary_learned_placeholder:"[What have you learned about how things work?]",xml_summary_completed_placeholder:"[What work has been completed so far? What has shipped or changed?]",xml_summary_next_steps_placeholder:"[What are you actively working on or planning to work on next in this session?]",xml_summary_notes_placeholder:"[Additional insights or observations about the current progress]",header_memory_start:`MEMORY PROCESSING START
=======================`,header_memory_continued:`MEMORY PROCESSING CONTINUED
===========================`,header_summary_checkpoint:`PROGRESS SUMMARY CHECKPOINT
===========================`,continuation_greeting:"[MEMORY] Hello memory agent, you are continuing to observe the primary Claude session.",continuation_instruction:"IMPORTANT: Continue generating observations from tool use messages using the XML structure below.",summary_instruction:`Write progress notes of what was done, what was learned, and what's next. This is a checkpoint to capture progress so far. The session is ongoing - you may receive more requests and tool executions after this summary. Write "next_steps" as the current trajectory of work (what's actively being worked on or coming up next), not as post-session future work. Always write at least a minimal summary explaining current progress, even if work is still in early stages, so that users see a summary output tied to each request.`,summary_context_label:"Claude's Full Response to User:",summary_format_instruction:"Respond in this XML format (ALL fields are REQUIRED - never leave any field empty):",summary_footer:`EXAMPLE of a complete, well-formed summary:
\`\`\`xml
<summary>
  <request>Implement user authentication with OAuth2 support</request>
  <investigated>Examined existing auth middleware, reviewed OAuth2 libraries (passport, grant), analyzed token storage options in Redis vs PostgreSQL</investigated>
  <learned>The app uses session-based auth with express-session. OAuth2 requires stateless JWT tokens. Passport.js supports both strategies simultaneously via passport-jwt and passport-oauth2 packages.</learned>
  <completed>Installed passport and passport-google-oauth20. Created OAuth2Strategy configuration in src/auth/strategies/google.ts. Added /auth/google and /auth/google/callback routes. Users can now sign in with Google.</completed>
  <next_steps>Adding GitHub OAuth provider next, then implementing token refresh logic</next_steps>
  <notes>Consider adding rate limiting to OAuth endpoints to prevent abuse</notes>
</summary>
\`\`\`

IMPORTANT! You MUST fill in ALL six fields (request, investigated, learned, completed, next_steps, notes) with actual content - never leave any field empty or use placeholder text. If a field doesn't apply, write a brief explanation why (e.g., "No investigation needed - straightforward implementation").

Do not output anything other than the summary content formatted in the XML structure above.`}},S=class r{static instance=null;activeMode=null;constructor(){}static getInstance(){return r.instance||(r.instance=new r),r.instance}loadMode(){return this.activeMode=he,he}getActiveMode(){if(!this.activeMode)throw new Error("No mode loaded. Call loadMode() first.");return this.activeMode}getObservationTypes(){return this.getActiveMode().observation_types}getObservationConcepts(){return this.getActiveMode().observation_concepts}getTypeIcon(e){return this.getObservationTypes().find(s=>s.id===e)?.emoji||"\u{1F4DD}"}getWorkEmoji(e){return this.getObservationTypes().find(s=>s.id===e)?.work_emoji||"\u{1F4DD}"}validateType(e){return this.getObservationTypes().some(t=>t.id===e)}getTypeLabel(e){return this.getObservationTypes().find(s=>s.id===e)?.label||e}};function K(r){let e=(r.title?.length||0)+(r.subtitle?.length||0)+(r.narrative?.length||0)+JSON.stringify(r.facts||[]).length;return Math.ceil(e/Te)}function J(r){let e=r.length,t=r.reduce((i,d)=>i+K(d),0),s=r.reduce((i,d)=>i+(d.discovery_tokens||0),0),n=s-t,o=s>0?Math.round(n/s*100):0;return{totalObservations:e,totalReadTokens:t,totalDiscoveryTokens:s,savings:n,savingsPercent:o}}function Ct(r){return S.getInstance().getWorkEmoji(r)}function v(r,e){let t=K(r),s=r.discovery_tokens||0,n=Ct(r.type),o=s>0?`${n} ${s.toLocaleString()}`:"-";return{readTokens:t,discoveryTokens:s,discoveryDisplay:o,workEmoji:n}}function j(r){return r.showReadTokens||r.showWorkTokens||r.showSavingsAmount||r.showSavingsPercent}var fe=C(require("path"),1),be=require("os"),X=require("fs");function z(r,e,t){let s=Array.from(t.observationTypes),n=s.map(()=>"?").join(","),o=Array.from(t.observationConcepts),i=o.map(()=>"?").join(",");return r.db.prepare(`
    SELECT
      id, memory_session_id, type, title, subtitle, narrative,
      facts, concepts, files_read, files_modified, discovery_tokens,
      created_at, created_at_epoch
    FROM observations
    WHERE project = ?
      AND type IN (${n})
      AND EXISTS (
        SELECT 1 FROM json_each(concepts)
        WHERE value IN (${i})
      )
    ORDER BY created_at_epoch DESC
    LIMIT ?
  `).all(e,...s,...o,t.totalObservationCount)}function Q(r,e,t){return r.db.prepare(`
    SELECT id, memory_session_id, request, investigated, learned, completed, next_steps, created_at, created_at_epoch
    FROM session_summaries
    WHERE project = ?
    ORDER BY created_at_epoch DESC
    LIMIT ?
  `).all(e,t.sessionCount+x)}function Oe(r,e,t){let s=Array.from(t.observationTypes),n=s.map(()=>"?").join(","),o=Array.from(t.observationConcepts),i=o.map(()=>"?").join(","),d=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT
      id, memory_session_id, type, title, subtitle, narrative,
      facts, concepts, files_read, files_modified, discovery_tokens,
      created_at, created_at_epoch, project
    FROM observations
    WHERE project IN (${d})
      AND type IN (${n})
      AND EXISTS (
        SELECT 1 FROM json_each(concepts)
        WHERE value IN (${i})
      )
    ORDER BY created_at_epoch DESC
    LIMIT ?
  `).all(...e,...s,...o,t.totalObservationCount)}function Se(r,e,t){let s=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT id, memory_session_id, request, investigated, learned, completed, next_steps, created_at, created_at_epoch, project
    FROM session_summaries
    WHERE project IN (${s})
    ORDER BY created_at_epoch DESC
    LIMIT ?
  `).all(...e,t.sessionCount+x)}function Ie(r,e,t,s){let n=Array.from(t.observationTypes),o=n.map(()=>"?").join(","),i=Array.from(t.observationConcepts),d=i.map(()=>"?").join(",");return r.db.prepare(`
    SELECT
      o.id, o.memory_session_id, o.type, o.title, o.subtitle, o.narrative,
      o.facts, o.concepts, o.files_read, o.files_modified, o.discovery_tokens,
      o.created_at, o.created_at_epoch
    FROM observations o
    LEFT JOIN sdk_sessions s ON o.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE o.project = ?
      AND o.type IN (${o})
      AND EXISTS (
        SELECT 1 FROM json_each(o.concepts)
        WHERE value IN (${d})
      )
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY o.created_at_epoch DESC
    LIMIT ?
  `).all(e,...n,...i,s,t.totalObservationCount)}function Re(r,e,t,s){return r.db.prepare(`
    SELECT ss.id, ss.memory_session_id, ss.request, ss.investigated, ss.learned,
           ss.completed, ss.next_steps, ss.created_at, ss.created_at_epoch
    FROM session_summaries ss
    LEFT JOIN sdk_sessions s ON ss.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE ss.project = ?
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY ss.created_at_epoch DESC
    LIMIT ?
  `).all(e,s,t.sessionCount+x)}function ye(r,e,t,s){let n=Array.from(t.observationTypes),o=n.map(()=>"?").join(","),i=Array.from(t.observationConcepts),d=i.map(()=>"?").join(","),a=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT
      o.id, o.memory_session_id, o.type, o.title, o.subtitle, o.narrative,
      o.facts, o.concepts, o.files_read, o.files_modified, o.discovery_tokens,
      o.created_at, o.created_at_epoch, o.project
    FROM observations o
    LEFT JOIN sdk_sessions s ON o.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE o.project IN (${a})
      AND o.type IN (${o})
      AND EXISTS (
        SELECT 1 FROM json_each(o.concepts)
        WHERE value IN (${d})
      )
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY o.created_at_epoch DESC
    LIMIT ?
  `).all(...e,...n,...i,s,t.totalObservationCount)}function Ne(r,e,t,s){let n=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT ss.id, ss.memory_session_id, ss.request, ss.investigated, ss.learned,
           ss.completed, ss.next_steps, ss.created_at, ss.created_at_epoch, ss.project
    FROM session_summaries ss
    LEFT JOIN sdk_sessions s ON ss.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE ss.project IN (${n})
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY ss.created_at_epoch DESC
    LIMIT ?
  `).all(...e,s,t.sessionCount+x)}function At(r){return r.replace(new RegExp("/","g"),"-")}function vt(r){try{if(!(0,X.existsSync)(r))return{userMessage:"",assistantMessage:""};let e=(0,X.readFileSync)(r,"utf-8").trim();if(!e)return{userMessage:"",assistantMessage:""};let t=e.split(`
`).filter(n=>n.trim()),s="";for(let n=t.length-1;n>=0;n--)try{let o=t[n];if(!o.includes('"type":"assistant"'))continue;let i=JSON.parse(o);if(i.type==="assistant"&&i.message?.content&&Array.isArray(i.message.content)){let d="";for(let a of i.message.content)a.type==="text"&&(d+=a.text);if(d=d.replace(/<system-reminder>[\s\S]*?<\/system-reminder>/g,"").trim(),d){s=d;break}}}catch(o){u.debug("PARSER","Skipping malformed transcript line",{lineIndex:n},o);continue}return{userMessage:"",assistantMessage:s}}catch(e){return u.failure("WORKER","Failed to extract prior messages from transcript",{transcriptPath:r},e),{userMessage:"",assistantMessage:""}}}function Z(r,e,t,s){if(!e.showLastMessage||r.length===0)return{userMessage:"",assistantMessage:""};let n=r.find(a=>a.memory_session_id!==t);if(!n)return{userMessage:"",assistantMessage:""};let o=n.memory_session_id,i=At(s),d=fe.default.join((0,be.homedir)(),".claude","projects",i,`${o}.jsonl`);return vt(d)}function Le(r,e){let t=e[0]?.id;return r.map((s,n)=>{let o=n===0?null:e[n+1];return{...s,displayEpoch:o?o.created_at_epoch:s.created_at_epoch,displayTime:o?o.created_at:s.created_at,shouldShowLink:s.id!==t}})}function ee(r,e){let t=[...r.map(s=>({type:"observation",data:s})),...e.map(s=>({type:"summary",data:s}))];return t.sort((s,n)=>{let o=s.type==="observation"?s.data.created_at_epoch:s.data.displayEpoch,i=n.type==="observation"?n.data.created_at_epoch:n.data.displayEpoch;return o-i}),t}function Ce(r,e){return new Set(r.slice(0,e).map(t=>t.id))}function Ae(){let r=new Date,e=r.toLocaleDateString("en-CA"),t=r.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0}).toLowerCase().replace(" ",""),s=r.toLocaleTimeString("en-US",{timeZoneName:"short"}).split(" ").pop();return`${e} ${t} ${s}`}function ve(r){return[`# [${r}] recent context, ${Ae()}`,""]}function De(){return[`**Legend:** session-request | ${S.getInstance().getActiveMode().observation_types.map(t=>`${t.emoji} ${t.id}`).join(" | ")}`,""]}function xe(){return["**Column Key**:","- **Read**: Tokens to read this observation (cost to learn it now)","- **Work**: Tokens spent on work that produced this record ( research, building, deciding)",""]}function Me(){return["**Context Index:** This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.","","When you need implementation details, rationale, or debugging context:","- Use MCP tools (search, get_observations) to fetch full observations on-demand","- Critical types ( bugfix, decision) often need detailed fetching","- Trust this index over re-reading code for past decisions and learnings",""]}function ke(r,e){let t=[];if(t.push("**Context Economics**:"),t.push(`- Loading: ${r.totalObservations} observations (${r.totalReadTokens.toLocaleString()} tokens to read)`),t.push(`- Work investment: ${r.totalDiscoveryTokens.toLocaleString()} tokens spent on research, building, and decisions`),r.totalDiscoveryTokens>0&&(e.showSavingsAmount||e.showSavingsPercent)){let s="- Your savings: ";e.showSavingsAmount&&e.showSavingsPercent?s+=`${r.savings.toLocaleString()} tokens (${r.savingsPercent}% reduction from reuse)`:e.showSavingsAmount?s+=`${r.savings.toLocaleString()} tokens`:s+=`${r.savingsPercent}% reduction from reuse`,t.push(s)}return t.push(""),t}function we(r){return[`### ${r}`,""]}function Ue(r){return[`**${r}**`,"| ID | Time | T | Title | Read | Work |","|----|------|---|-------|------|------|"]}function Pe(r,e,t){let s=r.title||"Untitled",n=S.getInstance().getTypeIcon(r.type),{readTokens:o,discoveryDisplay:i}=v(r,t),d=t.showReadTokens?`~${o}`:"",a=t.showWorkTokens?i:"";return`| #${r.id} | ${e||'"'} | ${n} | ${s} | ${d} | ${a} |`}function $e(r,e,t,s){let n=[],o=r.title||"Untitled",i=S.getInstance().getTypeIcon(r.type),{readTokens:d,discoveryDisplay:a}=v(r,s);n.push(`**#${r.id}** ${e||'"'} ${i} **${o}**`),t&&(n.push(""),n.push(t),n.push(""));let c=[];return s.showReadTokens&&c.push(`Read: ~${d}`),s.showWorkTokens&&c.push(`Work: ${a}`),c.length>0&&n.push(c.join(", ")),n.push(""),n}function Fe(r,e){let t=`${r.request||"Session started"} (${e})`;return[`**#S${r.id}** ${t}`,""]}function M(r,e){return e?[`**${r}**: ${e}`,""]:[]}function je(r){return r.assistantMessage?["","---","","**Previously**","",`A: ${r.assistantMessage}`,""]:[]}function Xe(r,e){return["",`Access ${Math.round(r/1e3)}k tokens of past research & decisions for just ${e.toLocaleString()}t. Use MCP search tools to access memories by ID.`]}function We(r){return`# [${r}] recent context, ${Ae()}

No previous sessions found for this project yet.`}function Be(){let r=new Date,e=r.toLocaleDateString("en-CA"),t=r.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0}).toLowerCase().replace(" ",""),s=r.toLocaleTimeString("en-US",{timeZoneName:"short"}).split(" ").pop();return`${e} ${t} ${s}`}function He(r){return["",`${p.bright}${p.cyan}[${r}] recent context, ${Be()}${p.reset}`,`${p.gray}${"\u2500".repeat(60)}${p.reset}`,""]}function Ge(){let e=S.getInstance().getActiveMode().observation_types.map(t=>`${t.emoji} ${t.id}`).join(" | ");return[`${p.dim}Legend: session-request | ${e}${p.reset}`,""]}function Ye(){return[`${p.bright}Column Key${p.reset}`,`${p.dim}  Read: Tokens to read this observation (cost to learn it now)${p.reset}`,`${p.dim}  Work: Tokens spent on work that produced this record ( research, building, deciding)${p.reset}`,""]}function Ve(){return[`${p.dim}Context Index: This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.${p.reset}`,"",`${p.dim}When you need implementation details, rationale, or debugging context:${p.reset}`,`${p.dim}  - Use MCP tools (search, get_observations) to fetch full observations on-demand${p.reset}`,`${p.dim}  - Critical types ( bugfix, decision) often need detailed fetching${p.reset}`,`${p.dim}  - Trust this index over re-reading code for past decisions and learnings${p.reset}`,""]}function qe(r,e){let t=[];if(t.push(`${p.bright}${p.cyan}Context Economics${p.reset}`),t.push(`${p.dim}  Loading: ${r.totalObservations} observations (${r.totalReadTokens.toLocaleString()} tokens to read)${p.reset}`),t.push(`${p.dim}  Work investment: ${r.totalDiscoveryTokens.toLocaleString()} tokens spent on research, building, and decisions${p.reset}`),r.totalDiscoveryTokens>0&&(e.showSavingsAmount||e.showSavingsPercent)){let s="  Your savings: ";e.showSavingsAmount&&e.showSavingsPercent?s+=`${r.savings.toLocaleString()} tokens (${r.savingsPercent}% reduction from reuse)`:e.showSavingsAmount?s+=`${r.savings.toLocaleString()} tokens`:s+=`${r.savingsPercent}% reduction from reuse`,t.push(`${p.green}${s}${p.reset}`)}return t.push(""),t}function Ke(r){return[`${p.bright}${p.cyan}${r}${p.reset}`,""]}function Je(r){return[`${p.dim}${r}${p.reset}`]}function ze(r,e,t,s){let n=r.title||"Untitled",o=S.getInstance().getTypeIcon(r.type),{readTokens:i,discoveryTokens:d,workEmoji:a}=v(r,s),c=t?`${p.dim}${e}${p.reset}`:" ".repeat(e.length),l=s.showReadTokens&&i>0?`${p.dim}(~${i}t)${p.reset}`:"",m=s.showWorkTokens&&d>0?`${p.dim}(${a} ${d.toLocaleString()}t)${p.reset}`:"";return`  ${p.dim}#${r.id}${p.reset}  ${c}  ${o}  ${n} ${l} ${m}`}function Qe(r,e,t,s,n){let o=[],i=r.title||"Untitled",d=S.getInstance().getTypeIcon(r.type),{readTokens:a,discoveryTokens:c,workEmoji:l}=v(r,n),m=t?`${p.dim}${e}${p.reset}`:" ".repeat(e.length),g=n.showReadTokens&&a>0?`${p.dim}(~${a}t)${p.reset}`:"",E=n.showWorkTokens&&c>0?`${p.dim}(${l} ${c.toLocaleString()}t)${p.reset}`:"";return o.push(`  ${p.dim}#${r.id}${p.reset}  ${m}  ${d}  ${p.bright}${i}${p.reset}`),s&&o.push(`    ${p.dim}${s}${p.reset}`),(g||E)&&o.push(`    ${g} ${E}`),o.push(""),o}function Ze(r,e){let t=`${r.request||"Session started"} (${e})`;return[`${p.yellow}#S${r.id}${p.reset} ${t}`,""]}function k(r,e,t){return e?[`${t}${r}:${p.reset} ${e}`,""]:[]}function et(r){return r.assistantMessage?["","---","",`${p.bright}${p.magenta}Previously${p.reset}`,"",`${p.dim}A: ${r.assistantMessage}${p.reset}`,""]:[]}function tt(r,e){let t=Math.round(r/1e3);return["",`${p.dim}Access ${t}k tokens of past research & decisions for just ${e.toLocaleString()}t. Use MCP search tools to access memories by ID.${p.reset}`]}function st(r){return`
${p.bright}${p.cyan}[${r}] recent context, ${Be()}${p.reset}
${p.gray}${"\u2500".repeat(60)}${p.reset}

${p.dim}No previous sessions found for this project yet.${p.reset}
`}function rt(r,e,t,s){let n=[];return s?n.push(...He(r)):n.push(...ve(r)),s?n.push(...Ge()):n.push(...De()),s?n.push(...Ye()):n.push(...xe()),s?n.push(...Ve()):n.push(...Me()),j(t)&&(s?n.push(...qe(e,t)):n.push(...ke(e,t))),n}var te=C(require("path"),1);function H(r){if(!r)return[];try{let e=JSON.parse(r);return Array.isArray(e)?e:[]}catch(e){return u.debug("PARSER","Failed to parse JSON array, using empty fallback",{preview:r?.substring(0,50)},e),[]}}function ot(r){return new Date(r).toLocaleString("en-US",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit",hour12:!0})}function it(r){return new Date(r).toLocaleString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0})}function at(r){return new Date(r).toLocaleString("en-US",{month:"short",day:"numeric",year:"numeric"})}function nt(r,e){return te.default.isAbsolute(r)?te.default.relative(e,r):r}function dt(r,e,t){let s=H(r);if(s.length>0)return nt(s[0],e);if(t){let n=H(t);if(n.length>0)return nt(n[0],e)}return"General"}function Dt(r){let e=new Map;for(let s of r){let n=s.type==="observation"?s.data.created_at:s.data.displayTime,o=at(n);e.has(o)||e.set(o,[]),e.get(o).push(s)}let t=Array.from(e.entries()).sort((s,n)=>{let o=new Date(s[0]).getTime(),i=new Date(n[0]).getTime();return o-i});return new Map(t)}function xt(r,e){return e.fullObservationField==="narrative"?r.narrative:r.facts?H(r.facts).join(`
`):null}function Mt(r,e,t,s,n,o){let i=[];o?i.push(...Ke(r)):i.push(...we(r));let d=null,a="",c=!1;for(let l of e)if(l.type==="summary"){c&&(i.push(""),c=!1,d=null,a="");let m=l.data,g=ot(m.displayTime);o?i.push(...Ze(m,g)):i.push(...Fe(m,g))}else{let m=l.data,g=dt(m.files_modified,n,m.files_read),E=it(m.created_at),T=E!==a,O=T?E:"";a=E;let _=t.has(m.id);if(g!==d&&(c&&i.push(""),o?i.push(...Je(g)):i.push(...Ue(g)),d=g,c=!0),_){let f=xt(m,s);o?i.push(...Qe(m,E,T,f,s)):(c&&!o&&(i.push(""),c=!1),i.push(...$e(m,O,f,s)),d=null)}else o?i.push(ze(m,E,T,s)):i.push(Pe(m,O,s))}return c&&i.push(""),i}function pt(r,e,t,s,n){let o=[],i=Dt(r);for(let[d,a]of i)o.push(...Mt(d,a,e,t,s,n));return o}function ct(r,e,t){return!(!r.showLastSummary||!e||!!!(e.investigated||e.learned||e.completed||e.next_steps)||t&&e.created_at_epoch<=t.created_at_epoch)}function lt(r,e){let t=[];return e?(t.push(...k("Investigated",r.investigated,p.blue)),t.push(...k("Learned",r.learned,p.yellow)),t.push(...k("Completed",r.completed,p.green)),t.push(...k("Next Steps",r.next_steps,p.magenta))):(t.push(...M("Investigated",r.investigated)),t.push(...M("Learned",r.learned)),t.push(...M("Completed",r.completed)),t.push(...M("Next Steps",r.next_steps))),t}function ut(r,e){return e?et(r):je(r)}function mt(r,e,t){return!j(e)||r.totalDiscoveryTokens<=0||r.savings<=0?[]:t?tt(r.totalDiscoveryTokens,r.totalReadTokens):Xe(r.totalDiscoveryTokens,r.totalReadTokens)}var kt=_t.default.join((0,Et.homedir)(),".claude","plugins","marketplaces","pilot","plugin",".install-version");function wt(){try{return new F}catch(r){if(r.code==="ERR_DLOPEN_FAILED"){try{(0,gt.unlinkSync)(kt)}catch(e){u.debug("SYSTEM","Marker file cleanup failed (may not exist)",{},e)}return u.error("SYSTEM","Native module rebuild needed - restart Claude Code to auto-fix"),null}throw r}}function Ut(r,e){return e?st(r):We(r)}function Pt(r,e,t,s,n,o,i){let d=[],a=J(e);d.push(...rt(r,a,s,i));let c=t.slice(0,s.sessionCount),l=Le(c,t),m=ee(e,l),g=Ce(e,s.fullObservationCount);d.push(...pt(m,g,s,n,i));let E=t[0],T=e[0];ct(s,E,T)&&d.push(...lt(E,i));let O=Z(e,s,o,n);return d.push(...ut(O,i)),d.push(...mt(a,s,i)),d.join(`
`).trimEnd()}async function se(r,e=!1){let t=q(),s=r?.cwd??process.cwd(),n=_e(s),o=r?.projects||[n],i=wt();if(!i)return"";try{let d=r?.planPath,a,c;return d?(a=o.length>1?ye(i,o,t,d):Ie(i,n,t,d),c=o.length>1?Ne(i,o,t,d):Re(i,n,t,d)):(a=o.length>1?Oe(i,o,t):z(i,n,t),c=o.length>1?Se(i,o,t):Q(i,n,t)),a.length===0&&c.length===0?Ut(n,e):Pt(n,a,c,t,s,r?.session_id,e)}finally{i.close()}}0&&(module.exports={generateContext});
