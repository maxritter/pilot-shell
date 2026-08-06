"use strict";var Tt=Object.create;var U=Object.defineProperty;var ht=Object.getOwnPropertyDescriptor;var ft=Object.getOwnPropertyNames;var bt=Object.getPrototypeOf,Ot=Object.prototype.hasOwnProperty;var St=(r,e)=>{for(var t in e)U(r,t,{get:e[t],enumerable:!0})},ee=(r,e,t,s)=>{if(e&&typeof e=="object"||typeof e=="function")for(let n of ft(e))!Ot.call(r,n)&&n!==t&&U(r,n,{get:()=>e[n],enumerable:!(s=ht(e,n))||s.enumerable});return r};var C=(r,e,t)=>(t=r!=null?Tt(bt(r)):{},ee(e||!r||!r.__esModule?U(t,"default",{value:r,enumerable:!0}):t,r)),Rt=r=>ee(U({},"__esModule",{value:!0}),r);var Ft={};St(Ft,{generateContext:()=>Z});module.exports=Rt(Ft);var Et=C(require("path"),1),gt=require("fs");var ue=require("bun:sqlite");var b=require("path"),ne=require("os"),D=require("fs");var oe=require("url");var R=require("fs"),P=require("path"),re=require("os");var te="bugfix,feature,refactor,discovery,decision,change",se="how-it-works,why-it-exists,what-changed,problem-solution,gotcha,pattern,trade-off";var A=class{static LEGACY_SKIP_TOOLS_DEFAULT="ListMcpResourcesTool,SlashCommand,Skill,TodoWrite,AskUserQuestion";static DEFAULTS={CLAUDE_PILOT_MODEL:"haiku",CLAUDE_PILOT_CONTEXT_OBSERVATIONS:"50",CLAUDE_PILOT_WORKER_PORT:"41777",CLAUDE_PILOT_WORKER_HOST:"127.0.0.1",CLAUDE_PILOT_WORKER_BIND:"127.0.0.1",CLAUDE_PILOT_SKIP_TOOLS:"ListMcpResourcesTool,SlashCommand,Skill,TodoWrite,AskUserQuestion,Read,Grep,Glob,NotebookRead,WebSearch,WebFetch,ToolSearch,TaskCreate,TaskUpdate,TaskList,TaskGet,TaskOutput,TaskStop,ScheduleWakeup,ShareOnboardingGuide",CLAUDE_PILOT_DATA_DIR:(0,P.join)((0,re.homedir)(),".pilot/memory"),CLAUDE_PILOT_LOG_LEVEL:"INFO",CLAUDE_PILOT_PYTHON_VERSION:"3.12",CLAUDE_CODE_PATH:"",CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS:!1,CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS:!1,CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT:!1,CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT:!1,CLAUDE_PILOT_CONTEXT_OBSERVATION_TYPES:te,CLAUDE_PILOT_CONTEXT_OBSERVATION_CONCEPTS:se,CLAUDE_PILOT_CONTEXT_FULL_COUNT:"10",CLAUDE_PILOT_CONTEXT_FULL_FIELD:"facts",CLAUDE_PILOT_CONTEXT_SESSION_COUNT:"10",CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY:!0,CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE:!0,CLAUDE_PILOT_FOLDER_CLAUDEMD_ENABLED:!1,CLAUDE_PILOT_FOLDER_MD_EXCLUDE:"[]",CLAUDE_PILOT_CHROMA_ENABLED:!0,CLAUDE_PILOT_VECTOR_DB:"chroma",CLAUDE_PILOT_EMBEDDING_MODEL:"Xenova/all-MiniLM-L6-v2",CLAUDE_PILOT_EXCLUDE_PROJECTS:"[]",CLAUDE_PILOT_REMOTE_TOKEN:"",CLAUDE_PILOT_RETENTION_ENABLED:!0,CLAUDE_PILOT_RETENTION_MAX_AGE_DAYS:"31",CLAUDE_PILOT_RETENTION_MAX_COUNT:"5000",CLAUDE_PILOT_RETENTION_EXCLUDE_TYPES:'["summary"]',CLAUDE_PILOT_RETENTION_SOFT_DELETE:!1,CLAUDE_PILOT_BATCH_SIZE:"5",CLAUDE_PILOT_VECTOR_DB_MAX_PHYSICAL_MB:"2048",CLAUDE_PILOT_VECTOR_DB_MAX_LOGICAL_MB:"51200"};static getAllDefaults(){return{...this.DEFAULTS}}static get(e){return this.DEFAULTS[e]}static getInt(e){let t=this.get(e);return parseInt(t,10)}static getBool(e){return this.get(e)==="true"}static loadFromFile(e){try{if(!(0,R.existsSync)(e)){let d=this.getAllDefaults();try{let l=(0,P.dirname)(e);(0,R.existsSync)(l)||(0,R.mkdirSync)(l,{recursive:!0}),(0,R.writeFileSync)(e,JSON.stringify(d,null,2),"utf-8"),console.error("[SETTINGS] Created settings file with defaults:",e)}catch(l){console.warn("[SETTINGS] Failed to create settings file, using in-memory defaults:",e,l)}return d}let t=(0,R.readFileSync)(e,"utf-8"),s=JSON.parse(t),n=s;if(s.env&&typeof s.env=="object"){n=s.env;try{(0,R.writeFileSync)(e,JSON.stringify(n,null,2),"utf-8"),console.error("[SETTINGS] Migrated settings file from nested to flat schema:",e)}catch(d){console.warn("[SETTINGS] Failed to auto-migrate settings file:",e,d)}}let o=["CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS","CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS","CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT","CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT","CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY","CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE","CLAUDE_PILOT_FOLDER_CLAUDEMD_ENABLED","CLAUDE_PILOT_CHROMA_ENABLED","CLAUDE_PILOT_RETENTION_ENABLED","CLAUDE_PILOT_RETENTION_SOFT_DELETE"],i={...this.DEFAULTS},a=!1;for(let d of Object.keys(this.DEFAULTS))if(n[d]!==void 0)if(o.includes(d)){let l=n[d];typeof l=="string"?(i[d]=l==="true",a=!0):i[d]=l}else i[d]=n[d];if(a)try{(0,R.writeFileSync)(e,JSON.stringify(i,null,2),"utf-8"),console.error("[SETTINGS] Migrated boolean settings from strings to actual booleans:",e)}catch(d){console.warn("[SETTINGS] Failed to auto-migrate boolean settings:",e,d)}if(i.CLAUDE_PILOT_SKIP_TOOLS===this.LEGACY_SKIP_TOOLS_DEFAULT){i.CLAUDE_PILOT_SKIP_TOOLS=this.DEFAULTS.CLAUDE_PILOT_SKIP_TOOLS;try{(0,R.writeFileSync)(e,JSON.stringify(i,null,2),"utf-8"),console.error("[SETTINGS] Upgraded CLAUDE_PILOT_SKIP_TOOLS to expanded default:",e)}catch(d){console.warn("[SETTINGS] Failed to persist CLAUDE_PILOT_SKIP_TOOLS upgrade:",e,d)}}return i}catch(t){return console.warn("[SETTINGS] Failed to load settings, using defaults:",e,t),this.getAllDefaults()}}};var Lt={};function It(){return typeof __dirname<"u"?__dirname:(0,b.dirname)((0,oe.fileURLToPath)(Lt.url))}var Bt=It(),y=A.get("CLAUDE_PILOT_DATA_DIR");function F(r){return process.env.CLAUDE_CONFIG_DIR||(0,b.join)(r||(0,ne.homedir)(),".claude")}function ie(r){return(0,b.join)(F(r),"projects")}var $=F(),Gt=(0,b.join)(y,"archives"),Yt=(0,b.join)(y,"logs"),Vt=(0,b.join)(y,"trash"),qt=(0,b.join)(y,"backups"),Kt=(0,b.join)(y,"modes"),Jt=(0,b.join)(y,"settings.json"),ae=(0,b.join)(y,"pilot-memory.db"),zt=(0,b.join)(y,"vector-db"),Qt=(0,b.join)($,"settings.json"),Zt=(0,b.join)($,"CLAUDE.md"),es=(0,b.join)($,".credentials.json"),yt=(0,b.join)($,"plugins"),ts=(0,b.join)(yt,"marketplaces","pilot");function de(r){(0,D.mkdirSync)(r,{recursive:!0})}var L=require("fs"),M=require("path"),le=require("os"),Y=(o=>(o[o.DEBUG=0]="DEBUG",o[o.INFO=1]="INFO",o[o.WARN=2]="WARN",o[o.ERROR=3]="ERROR",o[o.SILENT=4]="SILENT",o))(Y||{}),ce=(0,M.join)((0,le.homedir)(),".pilot/memory"),V=class{level=null;useColor;logFilePath=null;logFileInitialized=!1;constructor(){this.useColor=process.stdout.isTTY??!1}ensureLogFileInitialized(){if(!this.logFileInitialized){this.logFileInitialized=!0;try{let e=(0,M.join)(ce,"logs");(0,L.existsSync)(e)||(0,L.mkdirSync)(e,{recursive:!0});let t=new Date().toISOString().split("T")[0];this.logFilePath=(0,M.join)(e,`pilot-memory-${t}.log`)}catch(e){console.error("[LOGGER] Failed to initialize log file:",e),this.logFilePath=null}}}getLevel(){if(this.level===null)try{let e=(0,M.join)(ce,"settings.json");if((0,L.existsSync)(e)){let t=(0,L.readFileSync)(e,"utf-8"),n=(JSON.parse(t).CLAUDE_PILOT_LOG_LEVEL||"INFO").toUpperCase();this.level=Y[n]??1}else this.level=1}catch{this.level=1}return this.level}correlationId(e,t){return`obs-${e}-${t}`}sessionId(e){return`session-${e}`}formatData(e){if(e==null)return"";if(typeof e=="string")return e;if(typeof e=="number"||typeof e=="boolean")return e.toString();if(typeof e=="object"){if(e instanceof Error)return this.getLevel()===0?`${e.message}
${e.stack}`:e.message;if(Array.isArray(e))return`[${e.length} items]`;let t=Object.keys(e);return t.length===0?"{}":t.length<=3?JSON.stringify(e):`{${t.length} keys: ${t.slice(0,3).join(", ")}...}`}return String(e)}formatTool(e,t){if(!t)return e;let s=t;if(typeof t=="string")try{s=JSON.parse(t)}catch{s=t}if(e==="Bash"&&s.command)return`${e}(${s.command})`;if(s.file_path)return`${e}(${s.file_path})`;if(s.notebook_path)return`${e}(${s.notebook_path})`;if(e==="Glob"&&s.pattern)return`${e}(${s.pattern})`;if(e==="Grep"&&s.pattern)return`${e}(${s.pattern})`;if(s.url)return`${e}(${s.url})`;if(s.query)return`${e}(${s.query})`;if(e==="Task"){if(s.subagent_type)return`${e}(${s.subagent_type})`;if(s.description)return`${e}(${s.description})`}return e==="Skill"&&s.skill?`${e}(${s.skill})`:e==="LSP"&&s.operation?`${e}(${s.operation})`:e}formatTimestamp(e){let t=e.getFullYear(),s=String(e.getMonth()+1).padStart(2,"0"),n=String(e.getDate()).padStart(2,"0"),o=String(e.getHours()).padStart(2,"0"),i=String(e.getMinutes()).padStart(2,"0"),a=String(e.getSeconds()).padStart(2,"0"),d=String(e.getMilliseconds()).padStart(3,"0");return`${t}-${s}-${n} ${o}:${i}:${a}.${d}`}log(e,t,s,n,o){if(e<this.getLevel())return;this.ensureLogFileInitialized();let i=this.formatTimestamp(new Date),a=Y[e].padEnd(5),d=t.padEnd(6),l="";n?.correlationId?l=`[${n.correlationId}] `:n?.sessionId&&(l=`[session-${n.sessionId}] `);let u="";o!=null&&(o instanceof Error?u=this.getLevel()===0?`
${o.message}
${o.stack}`:` ${o.message}`:this.getLevel()===0&&typeof o=="object"?u=`
`+JSON.stringify(o,null,2):u=" "+this.formatData(o));let p="";if(n){let{sessionId:_,memorySessionId:E,correlationId:O,...T}=n;Object.keys(T).length>0&&(p=` {${Object.entries(T).map(([f,S])=>`${f}=${S}`).join(", ")}}`)}let g=`[${i}] [${a}] [${d}] ${l}${s}${p}${u}`;if(this.logFilePath)try{(0,L.appendFileSync)(this.logFilePath,g+`
`,"utf8")}catch(_){process.stderr.write(`[LOGGER] Failed to write to log file: ${_}
`),this.logFilePath=null}else process.stderr.write(g+`
`)}debug(e,t,s,n){this.log(0,e,t,s,n)}info(e,t,s,n){this.log(1,e,t,s,n)}warn(e,t,s,n){this.log(2,e,t,s,n)}error(e,t,s,n){this.log(3,e,t,s,n)}dataIn(e,t,s,n){this.info(e,`\u2192 ${t}`,s,n)}dataOut(e,t,s,n){this.info(e,`\u2190 ${t}`,s,n)}success(e,t,s,n){this.info(e,`\u2713 ${t}`,s,n)}failure(e,t,s,n){this.error(e,`\u2717 ${t}`,s,n)}timing(e,t,s,n){this.info(e,`\u23F1 ${t}`,n,{duration:`${s}ms`})}happyPathError(e,t,s,n,o=""){let l=((new Error().stack||"").split(`
`)[2]||"").match(/at\s+(?:.*\s+)?\(?([^:]+):(\d+):(\d+)\)?/),u=l?`${l[1].split("/").pop()}:${l[2]}`:"unknown",p={...s,location:u};return this.warn(e,`[HAPPY-PATH] ${t}`,p,n),o}},m=new V;var j=class{db;constructor(e=ae){e!==":memory:"&&de(y),this.db=new ue.Database(e),this.db.run("PRAGMA journal_mode = WAL"),this.db.run("PRAGMA synchronous = NORMAL"),this.db.run("PRAGMA foreign_keys = ON"),this.initializeSchema(),this.ensureWorkerPortColumn(),this.ensurePromptTrackingColumns(),this.removeSessionSummariesUniqueConstraint(),this.addObservationHierarchicalFields(),this.makeObservationsTextNullable(),this.createUserPromptsTable(),this.ensureDiscoveryTokensColumn(),this.createPendingMessagesTable(),this.renameSessionIdColumns(),this.repairSessionIdColumnRename(),this.addFailedAtEpochColumn(),this.ensureSessionPlansTable(),this.createProjectRootsTable(),this.ensureNotificationsTable(),this.addSessionAgentColumn(),this.addObservationSharedColumns()}initializeSchema(){this.db.run(`
      CREATE TABLE IF NOT EXISTS schema_versions (
        id INTEGER PRIMARY KEY,
        version INTEGER UNIQUE NOT NULL,
        applied_at TEXT NOT NULL
      )
    `);let e=this.db.prepare("SELECT version FROM schema_versions ORDER BY version").all();(e.length>0?Math.max(...e.map(s=>s.version)):0)===0&&(m.info("DB","Initializing fresh database with migration004"),this.db.run(`
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
      `),this.db.prepare("INSERT INTO schema_versions (version, applied_at) VALUES (?, ?)").run(4,new Date().toISOString()),m.info("DB","Migration004 applied successfully"))}ensureWorkerPortColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(5))return;this.db.query("PRAGMA table_info(sdk_sessions)").all().some(n=>n.name==="worker_port")||(this.db.run("ALTER TABLE sdk_sessions ADD COLUMN worker_port INTEGER"),m.debug("DB","Added worker_port column to sdk_sessions table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(5,new Date().toISOString())}ensurePromptTrackingColumns(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(6))return;this.db.query("PRAGMA table_info(sdk_sessions)").all().some(d=>d.name==="prompt_counter")||(this.db.run("ALTER TABLE sdk_sessions ADD COLUMN prompt_counter INTEGER DEFAULT 0"),m.debug("DB","Added prompt_counter column to sdk_sessions table")),this.db.query("PRAGMA table_info(observations)").all().some(d=>d.name==="prompt_number")||(this.db.run("ALTER TABLE observations ADD COLUMN prompt_number INTEGER"),m.debug("DB","Added prompt_number column to observations table")),this.db.query("PRAGMA table_info(session_summaries)").all().some(d=>d.name==="prompt_number")||(this.db.run("ALTER TABLE session_summaries ADD COLUMN prompt_number INTEGER"),m.debug("DB","Added prompt_number column to session_summaries table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(6,new Date().toISOString())}removeSessionSummariesUniqueConstraint(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(7))return;if(!this.db.query("PRAGMA index_list(session_summaries)").all().some(n=>n.unique===1)){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(7,new Date().toISOString());return}m.debug("DB","Removing UNIQUE constraint from session_summaries.memory_session_id"),this.db.run("PRAGMA foreign_keys = OFF"),this.db.run("BEGIN TRANSACTION"),this.db.run(`
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
    `),this.db.run("COMMIT"),this.db.run("PRAGMA foreign_keys = ON"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(7,new Date().toISOString()),m.debug("DB","Successfully removed UNIQUE constraint from session_summaries.memory_session_id")}addObservationHierarchicalFields(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(8))return;if(this.db.query("PRAGMA table_info(observations)").all().some(n=>n.name==="title")){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(8,new Date().toISOString());return}m.debug("DB","Adding hierarchical fields to observations table"),this.db.run(`
      ALTER TABLE observations ADD COLUMN title TEXT;
      ALTER TABLE observations ADD COLUMN subtitle TEXT;
      ALTER TABLE observations ADD COLUMN facts TEXT;
      ALTER TABLE observations ADD COLUMN narrative TEXT;
      ALTER TABLE observations ADD COLUMN concepts TEXT;
      ALTER TABLE observations ADD COLUMN files_read TEXT;
      ALTER TABLE observations ADD COLUMN files_modified TEXT;
    `),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(8,new Date().toISOString()),m.debug("DB","Successfully added hierarchical fields to observations table")}makeObservationsTextNullable(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(9))return;let s=this.db.query("PRAGMA table_info(observations)").all().find(n=>n.name==="text");if(!s||s.notnull===0){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(9,new Date().toISOString());return}m.debug("DB","Making observations.text nullable"),this.db.run("PRAGMA foreign_keys = OFF"),this.db.run("BEGIN TRANSACTION"),this.db.run(`
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
    `),this.db.run("COMMIT"),this.db.run("PRAGMA foreign_keys = ON"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(9,new Date().toISOString()),m.debug("DB","Successfully made observations.text nullable")}createUserPromptsTable(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(10))return;if(this.db.query("PRAGMA table_info(user_prompts)").all().length>0){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(10,new Date().toISOString());return}m.debug("DB","Creating user_prompts table with FTS5 support"),this.db.run("BEGIN TRANSACTION"),this.db.run(`
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
    `),this.db.run("COMMIT"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(10,new Date().toISOString()),m.debug("DB","Successfully created user_prompts table with FTS5 support")}ensureDiscoveryTokensColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(11))return;this.db.query("PRAGMA table_info(observations)").all().some(i=>i.name==="discovery_tokens")||(this.db.run("ALTER TABLE observations ADD COLUMN discovery_tokens INTEGER DEFAULT 0"),m.debug("DB","Added discovery_tokens column to observations table")),this.db.query("PRAGMA table_info(session_summaries)").all().some(i=>i.name==="discovery_tokens")||(this.db.run("ALTER TABLE session_summaries ADD COLUMN discovery_tokens INTEGER DEFAULT 0"),m.debug("DB","Added discovery_tokens column to session_summaries table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(11,new Date().toISOString())}createPendingMessagesTable(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(16))return;if(this.db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='pending_messages'").all().length>0){this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(16,new Date().toISOString());return}m.debug("DB","Creating pending_messages table"),this.db.run(`
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
    `),this.db.run("CREATE INDEX IF NOT EXISTS idx_pending_messages_session ON pending_messages(session_db_id)"),this.db.run("CREATE INDEX IF NOT EXISTS idx_pending_messages_status ON pending_messages(status)"),this.db.run("CREATE INDEX IF NOT EXISTS idx_pending_messages_claude_session ON pending_messages(content_session_id)"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(16,new Date().toISOString()),m.debug("DB","pending_messages table created successfully")}renameSessionIdColumns(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(17))return;m.debug("DB","Checking session ID columns for semantic clarity rename");let t=0,s=(n,o,i)=>{let a=this.db.query(`PRAGMA table_info(${n})`).all(),d=a.some(u=>u.name===o);return a.some(u=>u.name===i)?!1:d?(this.db.run(`ALTER TABLE ${n} RENAME COLUMN ${o} TO ${i}`),m.debug("DB",`Renamed ${n}.${o} to ${i}`),!0):(m.warn("DB",`Column ${o} not found in ${n}, skipping rename`),!1)};s("sdk_sessions","claude_session_id","content_session_id")&&t++,s("sdk_sessions","sdk_session_id","memory_session_id")&&t++,s("pending_messages","claude_session_id","content_session_id")&&t++,s("observations","sdk_session_id","memory_session_id")&&t++,s("session_summaries","sdk_session_id","memory_session_id")&&t++,s("user_prompts","claude_session_id","content_session_id")&&t++,this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(17,new Date().toISOString()),t>0?m.debug("DB",`Successfully renamed ${t} session ID columns`):m.debug("DB","No session ID column renames needed (already up to date)")}repairSessionIdColumnRename(){this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(19)||this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(19,new Date().toISOString())}addFailedAtEpochColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(20))return;this.db.query("PRAGMA table_info(pending_messages)").all().some(n=>n.name==="failed_at_epoch")||(this.db.run("ALTER TABLE pending_messages ADD COLUMN failed_at_epoch INTEGER"),m.debug("DB","Added failed_at_epoch column to pending_messages table")),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(20,new Date().toISOString())}ensureSessionPlansTable(){this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(21)||(this.db.run(`
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
    `),this.db.run("CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(is_read, created_at DESC)"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(24,new Date().toISOString()))}addSessionAgentColumn(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(25))return;this.db.query("PRAGMA table_info(sdk_sessions)").all().some(n=>n.name==="agent")||this.db.run("ALTER TABLE sdk_sessions ADD COLUMN agent TEXT DEFAULT 'claude'"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(25,new Date().toISOString())}upsertProjectRoot(e,t){this.db.prepare(`INSERT INTO project_roots (project, root_path, last_seen_at)
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
    `).get(e)||null}getObservationsByIds(e,t={}){if(e.length===0)return[];let{orderBy:s="date_desc",limit:n,project:o,type:i,concepts:a,files:d}=t,l=s==="date_asc"?"ASC":"DESC",u=n!=null?Math.trunc(Number(n)):void 0,p=u&&u>0?"LIMIT ?":"",g=e.map(()=>"?").join(","),_=[...e],E=[];if(o&&(E.push("project = ?"),_.push(o)),i)if(Array.isArray(i)){let h=i.map(()=>"?").join(",");E.push(`type IN (${h})`),_.push(...i)}else E.push("type = ?"),_.push(i);if(a){let h=Array.isArray(a)?a:[a],f=h.map(()=>"EXISTS (SELECT 1 FROM json_each(concepts) WHERE value = ?)");_.push(...h),E.push(`(${f.join(" OR ")})`)}if(d){let h=Array.isArray(d)?d:[d],f=h.map(()=>"(EXISTS (SELECT 1 FROM json_each(files_read) WHERE value LIKE ?) OR EXISTS (SELECT 1 FROM json_each(files_modified) WHERE value LIKE ?))");h.forEach(S=>{_.push(`%${S}%`,`%${S}%`)}),E.push(`(${f.join(" OR ")})`)}let O=E.length>0?`WHERE id IN (${g}) AND ${E.join(" AND ")}`:`WHERE id IN (${g})`;return u&&u>0&&_.push(u),this.db.prepare(`
      SELECT *
      FROM observations
      ${O}
      ORDER BY created_at_epoch ${l}
      ${p}
    `).all(..._)}deleteProjectData(e){return this.db.transaction(()=>{let s=this.db.prepare("SELECT COUNT(*) as count FROM observations WHERE project = ?").get(e).count;return this.db.prepare("DELETE FROM sdk_sessions WHERE project = ?").run(e),this.db.prepare("DELETE FROM observations WHERE project = ?").run(e),s})()}deleteObservation(e){return this.db.prepare("DELETE FROM observations WHERE id = ?").run(e).changes>0}deleteObservations(e){if(e.length===0)return 0;let t=e.map(()=>"?").join(",");return this.db.prepare(`DELETE FROM observations WHERE id IN (${t})`).run(...e).changes}getSummaryForSession(e){return this.db.prepare(`
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
    `).all(e),n=new Set,o=new Set;for(let i of s){if(i.files_read){let a=JSON.parse(i.files_read);Array.isArray(a)&&a.forEach(d=>n.add(d))}if(i.files_modified){let a=JSON.parse(i.files_modified);Array.isArray(a)&&a.forEach(d=>o.add(d))}}return{filesRead:Array.from(n),filesModified:Array.from(o)}}getSessionById(e){return this.db.prepare(`
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
    `).get(e).count}createSDKSession(e,t,s,n){let o=new Date,i=o.getTime(),a=crypto.randomUUID();return this.db.prepare(`
      INSERT OR IGNORE INTO sdk_sessions
      (content_session_id, memory_session_id, project, user_prompt, started_at, started_at_epoch, status, agent)
      VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
    `).run(e,a,t,s,o.toISOString(),i,n??"claude"),this.db.prepare(`
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
    `).get(e,t)?.prompt_text??null}storeObservation(e,t,s,n,o=0,i,a){let d=i??Date.now(),l=new Date(d).toISOString(),u=this.db.prepare(`
      INSERT INTO observations
      (memory_session_id, project, type, title, subtitle, facts, narrative, concepts,
       files_read, files_modified, prompt_number, discovery_tokens, created_at, created_at_epoch,
       shared_uid, shared_author)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `),p;try{p=u.run(e,t,s.type,s.title,s.subtitle,JSON.stringify(s.facts),s.narrative,JSON.stringify(s.concepts),JSON.stringify(s.files_read),JSON.stringify(s.files_modified),n||null,o,l,d,a?.uid??null,a?.author??null)}catch(g){if(a){let _=this.findObservationBySharedUid(a.uid);if(_)return{id:_.id,createdAtEpoch:d}}throw g}return{id:Number(p.lastInsertRowid),createdAtEpoch:d}}storeSummary(e,t,s,n,o=0,i){let a=i??Date.now(),d=new Date(a).toISOString(),u=this.db.prepare(`
      INSERT INTO session_summaries
      (memory_session_id, project, request, investigated, learned, completed,
       next_steps, notes, prompt_number, discovery_tokens, created_at, created_at_epoch)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(e,t,s.request,s.investigated,s.learned,s.completed,s.next_steps,s.notes,n||null,o,d,a);return{id:Number(u.lastInsertRowid),createdAtEpoch:a}}storeObservations(e,t,s,n,o,i=0,a){let d=a??Date.now(),l=new Date(d).toISOString();return this.db.transaction(()=>{let p=[],g=this.db.prepare(`
        INSERT INTO observations
        (memory_session_id, project, type, title, subtitle, facts, narrative, concepts,
         files_read, files_modified, prompt_number, discovery_tokens, created_at, created_at_epoch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);for(let E of s){let O=g.run(e,t,E.type,E.title,E.subtitle,JSON.stringify(E.facts),E.narrative,JSON.stringify(E.concepts),JSON.stringify(E.files_read),JSON.stringify(E.files_modified),o||null,i,l,d);p.push(Number(O.lastInsertRowid))}let _=null;if(n){let O=this.db.prepare(`
          INSERT INTO session_summaries
          (memory_session_id, project, request, investigated, learned, completed,
           next_steps, notes, prompt_number, discovery_tokens, created_at, created_at_epoch)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(e,t,n.request,n.investigated,n.learned,n.completed,n.next_steps,n.notes,o||null,i,l,d);_=Number(O.lastInsertRowid)}return{observationIds:p,summaryId:_,createdAtEpoch:d}})()}storeObservationsAndMarkComplete(e,t,s,n,o,i,a,d=0,l){let u=l??Date.now(),p=new Date(u).toISOString();return this.db.transaction(()=>{let _=[],E=this.db.prepare(`
        INSERT INTO observations
        (memory_session_id, project, type, title, subtitle, facts, narrative, concepts,
         files_read, files_modified, prompt_number, discovery_tokens, created_at, created_at_epoch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);for(let h of s){let f=E.run(e,t,h.type,h.title,h.subtitle,JSON.stringify(h.facts),h.narrative,JSON.stringify(h.concepts),JSON.stringify(h.files_read),JSON.stringify(h.files_modified),a||null,d,p,u);_.push(Number(f.lastInsertRowid))}let O;if(n){let f=this.db.prepare(`
          INSERT INTO session_summaries
          (memory_session_id, project, request, investigated, learned, completed,
           next_steps, notes, prompt_number, discovery_tokens, created_at, created_at_epoch)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(e,t,n.request,n.investigated,n.learned,n.completed,n.next_steps,n.notes,a||null,d,p,u);O=Number(f.lastInsertRowid)}return this.db.prepare(`
        UPDATE pending_messages
        SET
          status = 'processed',
          completed_at_epoch = ?,
          tool_input = NULL,
          tool_response = NULL
        WHERE id = ? AND status = 'processing'
      `).run(u,o),{observationIds:_,summaryId:O,createdAtEpoch:u}})()}getSessionSummariesByIds(e,t={}){if(e.length===0)return[];let{orderBy:s="date_desc",limit:n,project:o}=t,i=s==="date_asc"?"ASC":"DESC",a=n!=null?Math.trunc(Number(n)):void 0,d=a&&a>0?"LIMIT ?":"",l=e.map(()=>"?").join(","),u=[...e],p=o?`WHERE id IN (${l}) AND project = ?`:`WHERE id IN (${l})`;return o&&u.push(o),a&&a>0&&u.push(a),this.db.prepare(`
      SELECT * FROM session_summaries
      ${p}
      ORDER BY created_at_epoch ${i}
      ${d}
    `).all(...u)}getUserPromptsByIds(e,t={}){if(e.length===0)return[];let{orderBy:s="date_desc",limit:n,project:o}=t,i=s==="date_asc"?"ASC":"DESC",a=n!=null?Math.trunc(Number(n)):void 0,d=a&&a>0?"LIMIT ?":"",l=e.map(()=>"?").join(","),u=[...e],p=o?"AND s.project = ?":"";return o&&u.push(o),a&&a>0&&u.push(a),this.db.prepare(`
      SELECT
        up.*,
        s.project,
        s.memory_session_id
      FROM user_prompts up
      JOIN sdk_sessions s ON up.content_session_id = s.content_session_id
      WHERE up.id IN (${l}) ${p}
      ORDER BY up.created_at_epoch ${i}
      ${d}
    `).all(...u)}getTimelineAroundTimestamp(e,t=10,s=10,n){return this.getTimelineAroundObservation(null,e,t,s,n)}getTimelineAroundObservation(e,t,s=10,n=10,o){let i=o?"AND project = ?":"",a=o?[o]:[],d,l;if(e!==null){let T=`
        SELECT id, created_at_epoch
        FROM observations
        WHERE id <= ? ${i}
        ORDER BY id DESC
        LIMIT ?
      `,h=`
        SELECT id, created_at_epoch
        FROM observations
        WHERE id >= ? ${i}
        ORDER BY id ASC
        LIMIT ?
      `;try{let f=this.db.prepare(T).all(e,...a,s+1),S=this.db.prepare(h).all(e,...a,n+1);if(f.length===0&&S.length===0)return{observations:[],sessions:[],prompts:[]};d=f.length>0?f[f.length-1].created_at_epoch:t,l=S.length>0?S[S.length-1].created_at_epoch:t}catch(f){return m.error("DB","Error getting boundary observations",void 0,{error:f,project:o}),{observations:[],sessions:[],prompts:[]}}}else{let T=`
        SELECT created_at_epoch
        FROM observations
        WHERE created_at_epoch <= ? ${i}
        ORDER BY created_at_epoch DESC
        LIMIT ?
      `,h=`
        SELECT created_at_epoch
        FROM observations
        WHERE created_at_epoch >= ? ${i}
        ORDER BY created_at_epoch ASC
        LIMIT ?
      `;try{let f=this.db.prepare(T).all(t,...a,s),S=this.db.prepare(h).all(t,...a,n+1);if(f.length===0&&S.length===0)return{observations:[],sessions:[],prompts:[]};d=f.length>0?f[f.length-1].created_at_epoch:t,l=S.length>0?S[S.length-1].created_at_epoch:t}catch(f){return m.error("DB","Error getting boundary timestamps",void 0,{error:f,project:o}),{observations:[],sessions:[],prompts:[]}}}let u=`
      SELECT *
      FROM observations
      WHERE created_at_epoch >= ? AND created_at_epoch <= ? ${i}
      ORDER BY created_at_epoch ASC
    `,p=`
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
    `,_=this.db.prepare(u).all(d,l,...a),E=this.db.prepare(p).all(d,l,...a),O=this.db.prepare(g).all(d,l,...a);return{observations:_,sessions:E.map(T=>({id:T.id,memory_session_id:T.memory_session_id,project:T.project,request:T.request,completed:T.completed,next_steps:T.next_steps,created_at:T.created_at,created_at_epoch:T.created_at_epoch})),prompts:O.map(T=>({id:T.id,content_session_id:T.content_session_id,prompt_number:T.prompt_number,prompt_text:T.prompt_text,project:T.project,created_at:T.created_at,created_at_epoch:T.created_at_epoch}))}}getPromptById(e){return this.db.prepare(`
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
    `).get(e)||null}addObservationSharedColumns(){if(this.db.prepare("SELECT version FROM schema_versions WHERE version = ?").get(26))return;let t=this.db.query("PRAGMA table_info(observations)").all();t.some(s=>s.name==="shared_uid")||this.db.run("ALTER TABLE observations ADD COLUMN shared_uid TEXT"),t.some(s=>s.name==="shared_author")||this.db.run("ALTER TABLE observations ADD COLUMN shared_author TEXT"),this.db.run("CREATE UNIQUE INDEX IF NOT EXISTS idx_observations_shared_uid ON observations(shared_uid)"),this.db.prepare("INSERT OR IGNORE INTO schema_versions (version, applied_at) VALUES (?, ?)").run(26,new Date().toISOString())}getOrCreateSharedSession(e){let t=`shared-${e}`,s=`shared-content-${e}`;if(this.db.prepare("SELECT memory_session_id FROM sdk_sessions WHERE memory_session_id = ?").get(t))return t;let o=new Date;return this.db.prepare(`
      INSERT INTO sdk_sessions (memory_session_id, content_session_id, project, started_at, started_at_epoch, status, agent)
      VALUES (?, ?, ?, ?, ?, 'active', 'shared')
    `).run(t,s,e,o.toISOString(),o.getTime()),m.info("SESSION","Created shared-memory session",{memorySessionId:t,project:e}),t}getShareableObservations(e,t){if(t.length===0)return[];let s=t.map(()=>"?").join(",");return this.db.prepare(`
      SELECT id, type, title, subtitle, facts, narrative, concepts,
             files_read, files_modified, created_at, created_at_epoch, shared_uid
      FROM observations
      WHERE project = ? AND type IN (${s})
      ORDER BY created_at_epoch ASC, id ASC
    `).all(e,...t)}findObservationBySharedUid(e){return this.db.prepare("SELECT id FROM observations WHERE shared_uid = ?").get(e)??null}markObservationShared(e,t){this.db.prepare("UPDATE observations SET shared_uid = ? WHERE id = ?").run(t,e)}getOrCreateManualSession(e){let t=`manual-${e}`,s=`manual-content-${e}`;if(this.db.prepare("SELECT memory_session_id FROM sdk_sessions WHERE memory_session_id = ?").get(t))return t;let o=new Date;return this.db.prepare(`
      INSERT INTO sdk_sessions (memory_session_id, content_session_id, project, started_at, started_at_epoch, status)
      VALUES (?, ?, ?, ?, ?, 'active')
    `).run(t,s,e,o.toISOString(),o.getTime()),m.info("SESSION","Created manual session",{memorySessionId:t,project:e}),t}close(){this.db.close()}importSdkSession(e){let t=this.db.prepare("SELECT id FROM sdk_sessions WHERE content_session_id = ?").get(e.content_session_id);return t?{imported:!1,id:t.id}:{imported:!0,id:this.db.prepare(`
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
    `).run(...n).changes>0)}deleteTag(e){return this.db.prepare("DELETE FROM tags WHERE id = ?").run(e).changes>0}addTagsToObservation(e,t){let s=this.getObservationById(e);if(!s)return;let n=[];try{n=s.tags?JSON.parse(s.tags):[]}catch{n=[]}let o=t.map(d=>d.toLowerCase().trim()),i=[...new Set([...n,...o])];this.db.prepare("UPDATE observations SET tags = ? WHERE id = ?").run(JSON.stringify(i),e);for(let d of o)n.includes(d)||(this.getOrCreateTag(d),this.db.prepare("UPDATE tags SET usage_count = usage_count + 1 WHERE name = ?").run(d))}removeTagsFromObservation(e,t){let s=this.getObservationById(e);if(!s)return;let n=[];try{n=s.tags?JSON.parse(s.tags):[]}catch{n=[]}let o=t.map(d=>d.toLowerCase().trim()),i=n.filter(d=>!o.includes(d));this.db.prepare("UPDATE observations SET tags = ? WHERE id = ?").run(JSON.stringify(i),e);for(let d of o)n.includes(d)&&this.db.prepare("UPDATE tags SET usage_count = MAX(0, usage_count - 1) WHERE name = ?").run(d)}getObservationTags(e){let t=this.getObservationById(e);if(!t?.tags)return[];try{return JSON.parse(t.tags)}catch{return[]}}getObservationsByTags(e,t={}){let{matchAll:s=!1,limit:n=50,project:o}=t,i=e.map(u=>u.toLowerCase().trim()),a,d=[];return s?(a=`SELECT * FROM observations WHERE tags IS NOT NULL AND ${i.map(()=>"EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)").join(" AND ")}`,d.push(...i)):(a=`SELECT * FROM observations WHERE tags IS NOT NULL AND (${i.map(()=>"EXISTS (SELECT 1 FROM json_each(tags) WHERE value = ?)").join(" OR ")})`,d.push(...i)),o&&(a+=" AND project = ?",d.push(o)),a+=" ORDER BY created_at_epoch DESC LIMIT ?",d.push(n),this.db.prepare(a).all(...d)}getPopularTags(e=20){return this.db.prepare(`
      SELECT name, color, usage_count FROM tags
      WHERE usage_count > 0
      ORDER BY usage_count DESC
      LIMIT ?
    `).all(e)}suggestTagsForObservation(e){let t=this.getObservationById(e);if(!t)return[];let s=[];if(t.concepts)try{let n=JSON.parse(t.concepts);s.push(...n)}catch{typeof t.concepts=="string"&&s.push(...t.concepts.split(",").map(n=>n.trim()))}return t.type&&s.push(t.type),[...new Set(s.map(n=>n.toLowerCase().trim()))].filter(Boolean)}};var N=C(require("path"),1),q=C(require("fs"),1);function pe(r){if(!r||r.trim()==="")return m.warn("PROJECT_NAME","Empty cwd provided, using fallback",{cwd:r}),"unknown-project";let e=N.default.basename(r);if(e===""){if(process.platform==="win32"){let n=r.match(/^([A-Z]):\\/i);if(n){let i=`drive-${n[1].toUpperCase()}`;return m.info("PROJECT_NAME","Drive root detected",{cwd:r,projectName:i}),i}}return m.warn("PROJECT_NAME","Root directory detected, using fallback",{cwd:r}),"unknown-project"}let t=Nt(r);return t||e}function Nt(r){try{let e;try{e=q.default.statSync(r).isDirectory()?r:N.default.dirname(r)}catch{e=N.default.dirname(r)}let t=N.default.parse(e).root,s=0,n=20;for(;e!==t&&s<n;){let o=N.default.join(e,".git");try{if(q.default.existsSync(o))return N.default.basename(e)}catch{}e=N.default.dirname(e),s++}return null}catch{return null}}var me=C(require("path"),1),_e=require("os");function Ee(){let r=me.default.join((0,_e.homedir)(),".pilot/memory","settings.json"),e=A.loadFromFile(r),t=new Set(e.CLAUDE_PILOT_CONTEXT_OBSERVATION_TYPES.split(",").map(n=>n.trim()).filter(Boolean)),s=new Set(e.CLAUDE_PILOT_CONTEXT_OBSERVATION_CONCEPTS.split(",").map(n=>n.trim()).filter(Boolean));return{totalObservationCount:parseInt(e.CLAUDE_PILOT_CONTEXT_OBSERVATIONS,10),fullObservationCount:parseInt(e.CLAUDE_PILOT_CONTEXT_FULL_COUNT,10),sessionCount:parseInt(e.CLAUDE_PILOT_CONTEXT_SESSION_COUNT,10),showReadTokens:e.CLAUDE_PILOT_CONTEXT_SHOW_READ_TOKENS,showWorkTokens:e.CLAUDE_PILOT_CONTEXT_SHOW_WORK_TOKENS,showSavingsAmount:e.CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_AMOUNT,showSavingsPercent:e.CLAUDE_PILOT_CONTEXT_SHOW_SAVINGS_PERCENT,observationTypes:t,observationConcepts:s,fullObservationField:e.CLAUDE_PILOT_CONTEXT_FULL_FIELD,showLastSummary:e.CLAUDE_PILOT_CONTEXT_SHOW_LAST_SUMMARY,showLastMessage:e.CLAUDE_PILOT_CONTEXT_SHOW_LAST_MESSAGE}}var c={reset:"\x1B[0m",bright:"\x1B[1m",dim:"\x1B[2m",cyan:"\x1B[36m",green:"\x1B[32m",yellow:"\x1B[33m",blue:"\x1B[34m",magenta:"\x1B[35m",gray:"\x1B[90m",red:"\x1B[31m"},ge=4,k=1;var Te={name:"Code Development",description:"Software development and engineering work",version:"1.0.0",observation_types:[{id:"bugfix",label:"Bug Fix",description:"Something was broken, now fixed",emoji:"\u{1F534}",work_emoji:"\u{1F6E0}\uFE0F"},{id:"feature",label:"Feature",description:"New capability or functionality added",emoji:"\u{1F7E3}",work_emoji:"\u{1F6E0}\uFE0F"},{id:"refactor",label:"Refactor",description:"Code restructured, behavior unchanged",emoji:"\u{1F504}",work_emoji:"\u{1F6E0}\uFE0F"},{id:"change",label:"Change",description:"Generic modification (docs, config, misc)",emoji:"\u2705",work_emoji:"\u{1F6E0}\uFE0F"},{id:"discovery",label:"Discovery",description:"Learning about existing system",emoji:"\u{1F535}",work_emoji:"\u{1F50D}"},{id:"decision",label:"Decision",description:"Architectural/design choice with rationale",emoji:"\u2696\uFE0F",work_emoji:"\u2696\uFE0F"}],observation_concepts:[{id:"how-it-works",label:"How It Works",description:"Understanding mechanisms"},{id:"why-it-exists",label:"Why It Exists",description:"Purpose or rationale"},{id:"what-changed",label:"What Changed",description:"Modifications made"},{id:"problem-solution",label:"Problem-Solution",description:"Issues and their fixes"},{id:"gotcha",label:"Gotcha",description:"Traps or edge cases"},{id:"pattern",label:"Pattern",description:"Reusable approach"},{id:"trade-off",label:"Trade-Off",description:"Pros/cons of a decision"}],prompts:{system_identity:`[MEMORY] You are a specialized observer tool for creating searchable memory FOR FUTURE SESSIONS.

CRITICAL: Record what was LEARNED/BUILT/FIXED/DEPLOYED/CONFIGURED, not what you (the observer) are doing.

You do not have access to tools. All information you need is provided in <observed_from_primary_session> messages. Create observations from what you observe - no investigation needed.`,spatial_awareness:`SPATIAL AWARENESS: Tool executions include the working directory (tool_cwd) to help you understand:
- Which repository/project is being worked on
- Where files are located relative to the project root
- How to match requested paths to actual execution paths`,observer_role:"Your job is to monitor a different Claude Code session happening RIGHT NOW, with the goal of creating observations and progress summaries as the work is being done LIVE by the user. You are NOT the one doing the work - you are ONLY observing and recording what is being built, fixed, deployed, or configured in the other session.",recording_focus:`WHAT TO RECORD
--------------
DEFAULT POSTURE: SKIP. Record an observation ONLY when ALL THREE of these are true:

1. DURABLE: The fact remains true after this session ends (a new behaviour, a root cause, a design choice). Not a verification step, not a tool invocation, not a transient state.
2. NON-OBVIOUS: A future session in this project would be measurably worse off without it \u2014 they could not trivially re-derive it from the code, README, or git log.
3. CONCRETE: Names a specific file, function, system, or decision \u2014 not a generalisation about "the project" or "the work".

Use verbs like: implemented, fixed, deployed, configured, migrated, optimized, added, refactored, decided.

\u2705 RECORD (each names a concrete, durable, non-obvious fact):
- "Authentication now supports OAuth2 with PKCE flow via passport-google-oauth20"
- "Deployment pipeline runs canary releases with auto-rollback after 5xx > 1%"
- "Database indexes optimized for orders.created_at + customer_id query pattern"
- "Chose Redis over PostgreSQL for session storage due to 50ms TTL eviction requirement"

\u274C DO NOT RECORD (each is a verification step, exploration log, or activity report):
- "All tests pass after the refactor" \u2014 verification, not a durable fact
- "User investigating Semble search tools" \u2014 activity log, not a fact about the system
- "Test file has no staged changes" \u2014 transient git state
- "Committed X to main branch" \u2014 git history already records this
- "Pushed Y to GitHub" \u2014 operational event, not durable knowledge
- "Console source code reveals worker service architecture" \u2014 re-derivable from the code
- "install.sh download_installer filters for .py and .yaml files" \u2014 re-derivable from one grep`,skip_guidance:`WHEN TO SKIP (this is the common case)
--------------------------------------
DEFAULT TO SKIP. The bar for recording an observation is HIGH. Ask yourself: "Would a future session in this project be measurably worse off without this observation?" If the answer is anything other than a confident YES, skip.

MANDATORY SKIP for any of these:
- Tests pass / verification confirms / build succeeds / typecheck clean (verification is not knowledge)
- File reads, greps, globs, searches (exploration, not output)
- Git status / log / diff / show / branch inspection (transient state)
- Empty results, not-found responses, "nothing to commit" outcomes
- Activity log style: "user investigated X", "agent explored Y", "session looked at Z"
- Anything trivially re-derivable from one Read or one grep of the codebase
- Repetitive operations you've already documented in this session
- Commits, pushes, pulls \u2014 git history already records these durably

The cross-session test: imagine a brand-new session opens the project tomorrow with no memory. Will this observation save them work, or is it noise they'll have to scroll past? If the latter, skip.

IMPORTANT: If you decide to skip, output NOTHING AT ALL. Do not say 'no output needed' or explain why you're skipping. Simply produce zero output \u2014 an empty response. Skipping is the expected default, not a failure mode.`,type_guidance:`**type**: MUST be EXACTLY one of these 6 options (no other values allowed):
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

Do not output anything other than the summary content formatted in the XML structure above.`}},I=class r{static instance=null;activeMode=null;constructor(){}static getInstance(){return r.instance||(r.instance=new r),r.instance}loadMode(){return this.activeMode=Te,Te}getActiveMode(){if(!this.activeMode)throw new Error("No mode loaded. Call loadMode() first.");return this.activeMode}getObservationTypes(){return this.getActiveMode().observation_types}getObservationConcepts(){return this.getActiveMode().observation_concepts}getTypeIcon(e){return this.getObservationTypes().find(s=>s.id===e)?.emoji||"\u{1F4DD}"}getWorkEmoji(e){return this.getObservationTypes().find(s=>s.id===e)?.work_emoji||"\u{1F4DD}"}validateType(e){return this.getObservationTypes().some(t=>t.id===e)}getTypeLabel(e){return this.getObservationTypes().find(s=>s.id===e)?.label||e}};function K(r){let e=(r.title?.length||0)+(r.subtitle?.length||0)+(r.narrative?.length||0)+JSON.stringify(r.facts||[]).length;return Math.ceil(e/ge)}function J(r){let e=r.length,t=r.reduce((i,a)=>i+K(a),0),s=r.reduce((i,a)=>i+(a.discovery_tokens||0),0),n=s-t,o=s>0?Math.round(n/s*100):0;return{totalObservations:e,totalReadTokens:t,totalDiscoveryTokens:s,savings:n,savingsPercent:o}}function Ct(r){return I.getInstance().getWorkEmoji(r)}function v(r,e){let t=K(r),s=r.discovery_tokens||0,n=Ct(r.type),o=s>0?`${n} ${s.toLocaleString()}`:"-";return{readTokens:t,discoveryTokens:s,discoveryDisplay:o,workEmoji:n}}function X(r){return r.showReadTokens||r.showWorkTokens||r.showSavingsAmount||r.showSavingsPercent}var he=C(require("path"),1),W=require("fs");function fe(r,e,t){let s=Array.from(t.observationTypes),n=s.map(()=>"?").join(","),o=Array.from(t.observationConcepts),i=o.map(()=>"?").join(",");return r.db.prepare(`
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
  `).all(e,...s,...o,t.totalObservationCount)}function be(r,e,t){return r.db.prepare(`
    SELECT id, memory_session_id, request, investigated, learned, completed, next_steps, created_at, created_at_epoch
    FROM session_summaries
    WHERE project = ?
    ORDER BY created_at_epoch DESC
    LIMIT ?
  `).all(e,t.sessionCount+k)}function Oe(r,e,t){let s=Array.from(t.observationTypes),n=s.map(()=>"?").join(","),o=Array.from(t.observationConcepts),i=o.map(()=>"?").join(","),a=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT
      id, memory_session_id, type, title, subtitle, narrative,
      facts, concepts, files_read, files_modified, discovery_tokens,
      created_at, created_at_epoch, project
    FROM observations
    WHERE project IN (${a})
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
  `).all(...e,t.sessionCount+k)}function Re(r,e,t,s){let n=Array.from(t.observationTypes),o=n.map(()=>"?").join(","),i=Array.from(t.observationConcepts),a=i.map(()=>"?").join(",");return r.db.prepare(`
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
        WHERE value IN (${a})
      )
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY o.created_at_epoch DESC
    LIMIT ?
  `).all(e,...n,...i,s,t.totalObservationCount)}function Ie(r,e,t,s){return r.db.prepare(`
    SELECT ss.id, ss.memory_session_id, ss.request, ss.investigated, ss.learned,
           ss.completed, ss.next_steps, ss.created_at, ss.created_at_epoch
    FROM session_summaries ss
    LEFT JOIN sdk_sessions s ON ss.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE ss.project = ?
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY ss.created_at_epoch DESC
    LIMIT ?
  `).all(e,s,t.sessionCount+k)}function ye(r,e,t,s){let n=Array.from(t.observationTypes),o=n.map(()=>"?").join(","),i=Array.from(t.observationConcepts),a=i.map(()=>"?").join(","),d=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT
      o.id, o.memory_session_id, o.type, o.title, o.subtitle, o.narrative,
      o.facts, o.concepts, o.files_read, o.files_modified, o.discovery_tokens,
      o.created_at, o.created_at_epoch, o.project
    FROM observations o
    LEFT JOIN sdk_sessions s ON o.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE o.project IN (${d})
      AND o.type IN (${o})
      AND EXISTS (
        SELECT 1 FROM json_each(o.concepts)
        WHERE value IN (${a})
      )
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY o.created_at_epoch DESC
    LIMIT ?
  `).all(...e,...n,...i,s,t.totalObservationCount)}function Le(r,e,t,s){let n=e.map(()=>"?").join(",");return r.db.prepare(`
    SELECT ss.id, ss.memory_session_id, ss.request, ss.investigated, ss.learned,
           ss.completed, ss.next_steps, ss.created_at, ss.created_at_epoch, ss.project
    FROM session_summaries ss
    LEFT JOIN sdk_sessions s ON ss.memory_session_id = s.memory_session_id
    LEFT JOIN session_plans sp ON s.id = sp.session_db_id
    WHERE ss.project IN (${n})
      AND (sp.plan_path IS NULL OR sp.plan_path = ?)
    ORDER BY ss.created_at_epoch DESC
    LIMIT ?
  `).all(...e,s,t.sessionCount+k)}function At(r){return r.replace(new RegExp("/","g"),"-")}function vt(r){try{if(!(0,W.existsSync)(r))return{userMessage:"",assistantMessage:""};let e=(0,W.readFileSync)(r,"utf-8").trim();if(!e)return{userMessage:"",assistantMessage:""};let t=e.split(`
`).filter(n=>n.trim()),s="";for(let n=t.length-1;n>=0;n--)try{let o=t[n];if(!o.includes('"type":"assistant"'))continue;let i=JSON.parse(o);if(i.type==="assistant"&&i.message?.content&&Array.isArray(i.message.content)){let a="";for(let d of i.message.content)d.type==="text"&&(a+=d.text);if(a=a.replace(/<system-reminder>[\s\S]*?<\/system-reminder>/g,"").trim(),a){s=a;break}}}catch(o){m.debug("PARSER","Skipping malformed transcript line",{lineIndex:n},o);continue}return{userMessage:"",assistantMessage:s}}catch(e){return m.failure("WORKER","Failed to extract prior messages from transcript",{transcriptPath:r},e),{userMessage:"",assistantMessage:""}}}function Ne(r,e,t,s){if(!e.showLastMessage||r.length===0)return{userMessage:"",assistantMessage:""};let n=r.find(d=>d.memory_session_id!==t);if(!n)return{userMessage:"",assistantMessage:""};let o=n.memory_session_id,i=At(s),a=he.default.join(ie(),i,`${o}.jsonl`);return vt(a)}function Ce(r,e){let t=e[0]?.id;return r.map((s,n)=>{let o=n===0?null:e[n+1];return{...s,displayEpoch:o?o.created_at_epoch:s.created_at_epoch,displayTime:o?o.created_at:s.created_at,shouldShowLink:s.id!==t}})}function z(r,e){let t=[...r.map(s=>({type:"observation",data:s})),...e.map(s=>({type:"summary",data:s}))];return t.sort((s,n)=>{let o=s.type==="observation"?s.data.created_at_epoch:s.data.displayEpoch,i=n.type==="observation"?n.data.created_at_epoch:n.data.displayEpoch;return o-i}),t}function Ae(r,e){return new Set(r.slice(0,e).map(t=>t.id))}function ve(){let r=new Date,e=r.toLocaleDateString("en-CA"),t=r.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0}).toLowerCase().replace(" ",""),s=r.toLocaleTimeString("en-US",{timeZoneName:"short"}).split(" ").pop();return`${e} ${t} ${s}`}function De(r){return[`# [${r}] recent context, ${ve()}`,""]}function Me(){return[`**Legend:** session-request | ${I.getInstance().getActiveMode().observation_types.map(t=>`${t.emoji} ${t.id}`).join(" | ")}`,""]}function ke(){return["**Column Key**:","- **Read**: Tokens to read this observation (cost to learn it now)","- **Work**: Tokens spent on work that produced this record ( research, building, deciding)",""]}function xe(){return["**Context Index:** This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.","","When you need implementation details, rationale, or debugging context:","- Use MCP tools (search, get_observations) to fetch full observations on-demand","- Critical types ( bugfix, decision) often need detailed fetching","- Trust this index over re-reading code for past decisions and learnings",""]}function we(r,e){let t=[];if(t.push("**Context Economics**:"),t.push(`- Loading: ${r.totalObservations} observations (${r.totalReadTokens.toLocaleString()} tokens to read)`),t.push(`- Work investment: ${r.totalDiscoveryTokens.toLocaleString()} tokens spent on research, building, and decisions`),r.totalDiscoveryTokens>0&&(e.showSavingsAmount||e.showSavingsPercent)){let s="- Your savings: ";e.showSavingsAmount&&e.showSavingsPercent?s+=`${r.savings.toLocaleString()} tokens (${r.savingsPercent}% reduction from reuse)`:e.showSavingsAmount?s+=`${r.savings.toLocaleString()} tokens`:s+=`${r.savingsPercent}% reduction from reuse`,t.push(s)}return t.push(""),t}function Ue(r){return[`### ${r}`,""]}function Pe(r){return[`**${r}**`,"| ID | Time | T | Title | Read | Work |","|----|------|---|-------|------|------|"]}function Fe(r,e,t){let s=r.title||"Untitled",n=I.getInstance().getTypeIcon(r.type),{readTokens:o,discoveryDisplay:i}=v(r,t),a=t.showReadTokens?`~${o}`:"",d=t.showWorkTokens?i:"";return`| #${r.id} | ${e||'"'} | ${n} | ${s} | ${a} | ${d} |`}function $e(r,e,t,s){let n=[],o=r.title||"Untitled",i=I.getInstance().getTypeIcon(r.type),{readTokens:a,discoveryDisplay:d}=v(r,s);n.push(`**#${r.id}** ${e||'"'} ${i} **${o}**`),t&&(n.push(""),n.push(t),n.push(""));let l=[];return s.showReadTokens&&l.push(`Read: ~${a}`),s.showWorkTokens&&l.push(`Work: ${d}`),l.length>0&&n.push(l.join(", ")),n.push(""),n}function je(r,e){let t=`${r.request||"Session started"} (${e})`;return[`**#S${r.id}** ${t}`,""]}function x(r,e){return e?[`**${r}**: ${e}`,""]:[]}function Xe(r){return r.assistantMessage?["","---","","**Previously**","",`A: ${r.assistantMessage}`,""]:[]}function We(r,e){return["",`Access ${Math.round(r/1e3)}k tokens of past research & decisions for just ${e.toLocaleString()}t. Use MCP search tools to access memories by ID.`]}function He(r){return`# [${r}] recent context, ${ve()}

No previous sessions found for this project yet.`}function Be(){let r=new Date,e=r.toLocaleDateString("en-CA"),t=r.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0}).toLowerCase().replace(" ",""),s=r.toLocaleTimeString("en-US",{timeZoneName:"short"}).split(" ").pop();return`${e} ${t} ${s}`}function Ge(r){return["",`${c.bright}${c.cyan}[${r}] recent context, ${Be()}${c.reset}`,`${c.gray}${"\u2500".repeat(60)}${c.reset}`,""]}function Ye(){let e=I.getInstance().getActiveMode().observation_types.map(t=>`${t.emoji} ${t.id}`).join(" | ");return[`${c.dim}Legend: session-request | ${e}${c.reset}`,""]}function Ve(){return[`${c.bright}Column Key${c.reset}`,`${c.dim}  Read: Tokens to read this observation (cost to learn it now)${c.reset}`,`${c.dim}  Work: Tokens spent on work that produced this record ( research, building, deciding)${c.reset}`,""]}function qe(){return[`${c.dim}Context Index: This semantic index (titles, types, files, tokens) is usually sufficient to understand past work.${c.reset}`,"",`${c.dim}When you need implementation details, rationale, or debugging context:${c.reset}`,`${c.dim}  - Use MCP tools (search, get_observations) to fetch full observations on-demand${c.reset}`,`${c.dim}  - Critical types ( bugfix, decision) often need detailed fetching${c.reset}`,`${c.dim}  - Trust this index over re-reading code for past decisions and learnings${c.reset}`,""]}function Ke(r,e){let t=[];if(t.push(`${c.bright}${c.cyan}Context Economics${c.reset}`),t.push(`${c.dim}  Loading: ${r.totalObservations} observations (${r.totalReadTokens.toLocaleString()} tokens to read)${c.reset}`),t.push(`${c.dim}  Work investment: ${r.totalDiscoveryTokens.toLocaleString()} tokens spent on research, building, and decisions${c.reset}`),r.totalDiscoveryTokens>0&&(e.showSavingsAmount||e.showSavingsPercent)){let s="  Your savings: ";e.showSavingsAmount&&e.showSavingsPercent?s+=`${r.savings.toLocaleString()} tokens (${r.savingsPercent}% reduction from reuse)`:e.showSavingsAmount?s+=`${r.savings.toLocaleString()} tokens`:s+=`${r.savingsPercent}% reduction from reuse`,t.push(`${c.green}${s}${c.reset}`)}return t.push(""),t}function Je(r){return[`${c.bright}${c.cyan}${r}${c.reset}`,""]}function ze(r){return[`${c.dim}${r}${c.reset}`]}function Qe(r,e,t,s){let n=r.title||"Untitled",o=I.getInstance().getTypeIcon(r.type),{readTokens:i,discoveryTokens:a,workEmoji:d}=v(r,s),l=t?`${c.dim}${e}${c.reset}`:" ".repeat(e.length),u=s.showReadTokens&&i>0?`${c.dim}(~${i}t)${c.reset}`:"",p=s.showWorkTokens&&a>0?`${c.dim}(${d} ${a.toLocaleString()}t)${c.reset}`:"";return`  ${c.dim}#${r.id}${c.reset}  ${l}  ${o}  ${n} ${u} ${p}`}function Ze(r,e,t,s,n){let o=[],i=r.title||"Untitled",a=I.getInstance().getTypeIcon(r.type),{readTokens:d,discoveryTokens:l,workEmoji:u}=v(r,n),p=t?`${c.dim}${e}${c.reset}`:" ".repeat(e.length),g=n.showReadTokens&&d>0?`${c.dim}(~${d}t)${c.reset}`:"",_=n.showWorkTokens&&l>0?`${c.dim}(${u} ${l.toLocaleString()}t)${c.reset}`:"";return o.push(`  ${c.dim}#${r.id}${c.reset}  ${p}  ${a}  ${c.bright}${i}${c.reset}`),s&&o.push(`    ${c.dim}${s}${c.reset}`),(g||_)&&o.push(`    ${g} ${_}`),o.push(""),o}function et(r,e){let t=`${r.request||"Session started"} (${e})`;return[`${c.yellow}#S${r.id}${c.reset} ${t}`,""]}function w(r,e,t){return e?[`${t}${r}:${c.reset} ${e}`,""]:[]}function tt(r){return r.assistantMessage?["","---","",`${c.bright}${c.magenta}Previously${c.reset}`,"",`${c.dim}A: ${r.assistantMessage}${c.reset}`,""]:[]}function st(r,e){let t=Math.round(r/1e3);return["",`${c.dim}Access ${t}k tokens of past research & decisions for just ${e.toLocaleString()}t. Use MCP search tools to access memories by ID.${c.reset}`]}function rt(r){return`
${c.bright}${c.cyan}[${r}] recent context, ${Be()}${c.reset}
${c.gray}${"\u2500".repeat(60)}${c.reset}

${c.dim}No previous sessions found for this project yet.${c.reset}
`}function nt(r,e,t,s){let n=[];return s?n.push(...Ge(r)):n.push(...De(r)),s?n.push(...Ye()):n.push(...Me()),s?n.push(...Ve()):n.push(...ke()),s?n.push(...qe()):n.push(...xe()),X(t)&&(s?n.push(...Ke(e,t)):n.push(...we(e,t))),n}var Q=C(require("path"),1);function G(r){if(!r)return[];try{let e=JSON.parse(r);return Array.isArray(e)?e:[]}catch(e){return m.debug("PARSER","Failed to parse JSON array, using empty fallback",{preview:r?.substring(0,50)},e),[]}}function it(r){return new Date(r).toLocaleString("en-US",{month:"short",day:"numeric",hour:"numeric",minute:"2-digit",hour12:!0})}function at(r){return new Date(r).toLocaleString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0})}function dt(r){return new Date(r).toLocaleString("en-US",{month:"short",day:"numeric",year:"numeric"})}function ot(r,e){return Q.default.isAbsolute(r)?Q.default.relative(e,r):r}function ct(r,e,t){let s=G(r);if(s.length>0)return ot(s[0],e);if(t){let n=G(t);if(n.length>0)return ot(n[0],e)}return"General"}function Dt(r){let e=new Map;for(let s of r){let n=s.type==="observation"?s.data.created_at:s.data.displayTime,o=dt(n);e.has(o)||e.set(o,[]),e.get(o).push(s)}let t=Array.from(e.entries()).sort((s,n)=>{let o=new Date(s[0]).getTime(),i=new Date(n[0]).getTime();return o-i});return new Map(t)}function Mt(r,e){return e.fullObservationField==="narrative"?r.narrative:r.facts?G(r.facts).join(`
`):null}function kt(r,e,t,s,n,o){let i=[];o?i.push(...Je(r)):i.push(...Ue(r));let a=null,d="",l=!1;for(let u of e)if(u.type==="summary"){l&&(i.push(""),l=!1,a=null,d="");let p=u.data,g=it(p.displayTime);o?i.push(...et(p,g)):i.push(...je(p,g))}else{let p=u.data,g=ct(p.files_modified,n,p.files_read),_=at(p.created_at),E=_!==d,O=E?_:"";d=_;let T=t.has(p.id);if(g!==a&&(l&&i.push(""),o?i.push(...ze(g)):i.push(...Pe(g)),a=g,l=!0),T){let h=Mt(p,s);o?i.push(...Ze(p,_,E,h,s)):(l&&!o&&(i.push(""),l=!1),i.push(...$e(p,O,h,s)),a=null)}else o?i.push(Qe(p,_,E,s)):i.push(Fe(p,O,s))}return l&&i.push(""),i}function lt(r,e,t,s,n){let o=[],i=Dt(r);for(let[a,d]of i)o.push(...kt(a,d,e,t,s,n));return o}function ut(r,e,t){return!(!r.showLastSummary||!e||!!!(e.investigated||e.learned||e.completed||e.next_steps)||t&&e.created_at_epoch<=t.created_at_epoch)}function pt(r,e){let t=[];return e?(t.push(...w("Investigated",r.investigated,c.blue)),t.push(...w("Learned",r.learned,c.yellow)),t.push(...w("Completed",r.completed,c.green)),t.push(...w("Next Steps",r.next_steps,c.magenta))):(t.push(...x("Investigated",r.investigated)),t.push(...x("Learned",r.learned)),t.push(...x("Completed",r.completed)),t.push(...x("Next Steps",r.next_steps))),t}function mt(r,e){return e?tt(r):Xe(r)}function _t(r,e,t){return!X(e)||r.totalDiscoveryTokens<=0||r.savings<=0?[]:t?st(r.totalDiscoveryTokens,r.totalReadTokens):We(r.totalDiscoveryTokens,r.totalReadTokens)}var xt=Et.default.join(F(),"plugins","marketplaces","pilot","plugin",".install-version");function wt(){try{return new j}catch(r){if(r.code==="ERR_DLOPEN_FAILED"){try{(0,gt.unlinkSync)(xt)}catch(e){m.debug("SYSTEM","Marker file cleanup failed (may not exist)",{},e)}return m.error("SYSTEM","Native module rebuild needed - restart Claude Code to auto-fix"),null}throw r}}function Ut(r,e){return e?rt(r):He(r)}function Pt(r,e,t,s,n,o,i){let a=[],d=J(e);a.push(...nt(r,d,s,i));let l=t.slice(0,s.sessionCount),u=Ce(l,t),p=z(e,u),g=Ae(e,s.fullObservationCount);a.push(...lt(p,g,s,n,i));let _=t[0],E=e[0];ut(s,_,E)&&a.push(...pt(_,i));let O=Ne(e,s,o,n);return a.push(...mt(O,i)),a.push(..._t(d,s,i)),a.join(`
`).trimEnd()}async function Z(r,e=!1){let t=Ee(),s=r?.cwd??process.cwd(),n=pe(s),o=r?.projects||[n],i=wt();if(!i)return"";try{let a=r?.planPath,d,l;return a?(d=o.length>1?ye(i,o,t,a):Re(i,n,t,a),l=o.length>1?Le(i,o,t,a):Ie(i,n,t,a)):(d=o.length>1?Oe(i,o,t):fe(i,n,t),l=o.length>1?Se(i,o,t):be(i,n,t)),d.length===0&&l.length===0?Ut(n,e):Pt(n,d,l,t,s,r?.session_id,e)}finally{i.close()}}0&&(module.exports={generateContext});
