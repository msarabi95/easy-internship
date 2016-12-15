/**
 * Created by MSArabi on 12/10/16.
 */
exports.config = {
  seleniumAddress: 'http://localhost:4444/wd/hub',
  specs: [
      'intern/specs.intern.rotations.js'
  ],
  capabilities: {
    browserName: 'firefox'
  }
};