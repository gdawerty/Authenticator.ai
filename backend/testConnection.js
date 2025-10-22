import { connectAuthDB } from "./dbConnection.js";

const test = async () => {
  try {
    const pool = await connectAuthDB();
    
    // List existing databases
    const result = await pool.request().query("SELECT name FROM sys.databases");
    console.log("Connected! Databases:", result.recordset);
    
    // Create databases if they don't exist
    const databases = ['auth_db', 'docs_db', 'clones_db'];
    
    for (const dbName of databases) {
      const exists = result.recordset.some(db => db.name === dbName);
      if (!exists) {
        await pool.request().query(`CREATE DATABASE ${dbName}`);
        console.log(`✅ Created database: ${dbName}`);
      } else {
        console.log(`✅ Database exists: ${dbName}`);
      }
    }
    
  } catch (err) {
    console.error("❌ Connection failed:", err);
  }
};

test();
