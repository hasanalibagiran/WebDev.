const Koa = require('koa');
const app = new Koa();

// response
app.use(ctx => {
  if (ctx.path==='/'){
    ctx.body = '<h1>INDEX SAYFASINA HOSGELDINIZ</h1>';
  }
  else if (ctx.path==='/index'){
    ctx.body = '<h1>INDEX SAYFASINA HOSGELDINIZ</h1>';

  }
  else if (ctx.path==='/hakkimda'){
    ctx.body = '<h1>hakkımda SAYFASINA HOSGELDINIZ</h1>';

  }
  else if (ctx.path==='/iletisim'){
    ctx.body = '<h1>iletisim SAYFASINA HOSGELDINIZ</h1>';

  }
  else{
    ctx.body = '404 not found';
  }

});

app.listen(3000)    