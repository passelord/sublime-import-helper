'use strict';
const assert = require('assert');
const Path = require('path');
const pkgDir = require('pkg-dir');

const getFoldersCmd = require('./commands/get_folders');
const getModulesCmd = require('./commands/get_modules');
const ping = require('./commands/ping');
const removeUnused = require('./commands/remove_unused');
const getFromPackage = require('./commands/get_from_package');

const rootPath = pkgDir.sync(__dirname);

it('smoke test', () => {
    assert(true);
});

it('ping', done => {
    ping({}, (err, response) => {
        if (err) throw err;
        assert(response.message === 'Pong');
        assert(response.date);
        done();
    });
});

it('get folders importRoot will bed added if not folders', () => {
    var importRoot = Path.join(rootPath, 'test_playground');
    return getFoldersCmd({
        folders: [],
        importRoot: importRoot
    }, (err, response) => {
        assert.ifError(err);
        assert(response);
        assert(response.length > 0);
    });
});

it('get folders no pkg', () => {
    var importRoot = Path.join(rootPath, 'test_playground/no_pkg');
    return getFoldersCmd({
        folders: [],
        importRoot: importRoot,
    }, (err, result) => {
        assert.ifError(err);
        assert.deepEqual(result, []);
    });
});

it('get packages with broken json', () => {
    var importRoot = Path.join(rootPath, 'test_playground/bad_json');
    return getFoldersCmd({
        folders: [],
        importRoot: importRoot
    }, (err, response) => {
        assert.ifError(err);
        assert.deepEqual(response, []);
    });
});

it('get packages with empty_pkg', () => {
    var importRoot = Path.join(rootPath, 'test_playground/empty_pkg');
    return getFoldersCmd({
        folders: [],
        importRoot: importRoot
    }, (err, response) => {
        assert.ifError(err);
        assert.deepEqual(response, []);
    });
});

it('get packages with empty_file', () => {
    var importRoot = Path.join(rootPath, 'test_playground/empty_file');
    return getFoldersCmd({
        folders: [],
        importRoot: importRoot
    }, (err, response) => {
        assert.ifError(err);
        assert.deepEqual(response, []);
    });
});

it('get packages source only (ignore node_modules)', () => {
    return getFoldersCmd({
        folders: [rootPath],
    }, (err, response) => {
        assert.ifError(err);
        assert(response);
        assert(response.length);
        let [greeter] = response.filter(x => x.name === 'Greeter');
        assert(greeter);
    });
});

it('get_folders command', (done) => {
    const folder1 = Path.join(rootPath, 'test_playground/component');
    const folder2 = Path.join(rootPath, 'test_playground/lib');
    getFoldersCmd({
        folders: [folder1, folder2],
    }, (err, result) => {
        if (err) return done(err);
        assert(result.find(m => m.name === 'Animal'));
        assert(result.find(m => m.name === 'AbcComponent'));
        assert(result.filter(m => m.name === 'x2').length > 1);
        done();
    });
});

it('get_folders command with ignore patterns', (done) => {
    const folder1 = Path.join(rootPath, 'test_playground/app/t1');
    const folder2 = Path.join(rootPath, 'test_playground/app/t2');
    const ignore = {
        [folder1]: ['**/volumes'],
        [folder2]: ['dummy.component.ts'],
    };

    getFoldersCmd({
        folders: [folder1, folder2],
        ignore,
    }, (err, result) => {
        if (err) return done(err);

        let hasTest = false;
        let numX2 = 0;
        let hasVolume = false;
        let hasDummy = false;
        result.forEach(({ filepath, name }) => {
            if (name === 'test') {
                hasTest = true;
            }
            if (name === 'x2') {
                numX2++;
            }
            if (name === 'VOLUME' || filepath.indexOf('/volumes/') !== -1) {
                hasVolume = true;
            }
            if (name === 'DummyComponent' || /dummy\.component\.ts$/.test(filepath)) {
                hasDummy = true;
            }
        });
        assert(hasTest === true);
        assert(numX2 > 1);
        assert(hasVolume === false);
        assert(hasDummy === false);
        done();
    });
});

it('get_modules command', (done) => {
    getModulesCmd({

    }, (err, result) => {
        if (err) return done(err);
        assert(result.find(m => m.name === 'esmExports')); // esm-exports
        assert(result.find(m => m.name === 'Component')); // @angular/core
        assert(result.find(m => m.name === 'inject')); // @angular/core/testing
        done();
    });
});

it('get only dependencies', () => {
    getModulesCmd({
        packageKeys: ['dependencies'],
    }, (err, result) => {
        assert.ifError(err);
        assert.deepEqual(result, []);
    });
});

it('get folders error', () => {
    return getFoldersCmd({
        folders: null,
        importRoot: 'foobar',
    }, (err, response) => {
        assert(err);
        assert.ifError(response);
    });
});

describe('if error undefined we should set it to unknown err', () => {

    before(() => {
        const esm = require('esm-exports');
        esm.module = () => Promise.reject(undefined);
        esm.directory = () => Promise.reject(undefined);
    });

    after(() => {
        delete require.cache[require.resolve('esm-exports')];
    });

    it('get modules', () => {
        return getModulesCmd({
        }, (err) => {
            assert(err);
        });
    });

    it('get folders', () => {
        return getFoldersCmd({
            folders: [],
            importRoot: Path.join(rootPath, 'test_playground')
        }, (err) => {
            assert(err);
        });
    });
});

it('remove_unused', (done) => {
    removeUnused({
        file_name: 'test_playground/unused.ts',
    }, (err, result) => {
        if (err) {
            return done(err);
        }
        assert(Object.keys(result).length > 0);
        assert.equal(result[3][0].name, 'f');
        assert.equal(result[2][0].name, 'gr1');
        assert.equal(result[6][0].name, 'gr');
        assert.equal(result[8][0].name, 'someLib1');
        assert.equal(result[9][0].name, 'someLib2');

        assert.equal(result[4][0].all, true);

        done();
    });
});

it('get from package', (done) => {
    getFromPackage({ importRoot: rootPath }, (err, result) => {
        if (err) {
            return done(err);
        }
        assert(result);
        assert(result.length > 0);
        done();
    });
});
