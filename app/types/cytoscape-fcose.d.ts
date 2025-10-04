/**
 * Type declarations for cytoscape-fcose
 * 
 * This file provides TypeScript type definitions for the cytoscape-fcose library.
 * The fcose layout is a force-directed layout algorithm for Cytoscape.js
 */

declare module 'cytoscape-fcose' {
  import { Ext } from 'cytoscape';
  
  /**
   * fcose layout extension for Cytoscape
   * Provides a force-directed graph layout algorithm
   */
  const fcose: Ext;
  export default fcose;
}

