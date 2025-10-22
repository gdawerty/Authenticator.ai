import sql from "mssql";
import dotenv from "dotenv";
dotenv.config();

const dbConfig = {
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  server: process.env.DB_SERVER,
  options: { encrypt: false, trustServerCertificate: true }
};

export const connectAuthDB = () => sql.connect({
  ...dbConfig,
  database: "master"  // Connect to master first to create databases
});

export const connectDocsDB = () => sql.connect({
  ...dbConfig,
  database: "docs_db"
});

export const connectClonesDB = () => sql.connect({
  ...dbConfig,
  database: "clones_db"
});
