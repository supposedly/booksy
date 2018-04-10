// Made under partial guidance of a wonderful article by Netanel Basal:
// https://netbasal.com/create-advanced-components-in-angular-e0655df5dde6
import {
  ComponentFactoryResolver,
  ComponentRef,
  Directive,
  ElementRef,
  HostListener,
  Injector,
  Input,
  // FIXME: ReflectiveInjector is deprecated: from v5 - slow and brings in a lot of code, Use `Injector.create` instead.
  // So maybe I can just switch out the below `ReflectiveInjector.resolveAndCreate` with `Injector.create`...?
  ReflectiveInjector,
  Renderer2,
  ViewContainerRef,
  OnDestroy,
} from '@angular/core';
import { TooltipComponent } from './tooltip.component';

@Directive({
  // tslint:disable-next-line:directive-selector
  selector: '[tooltip]'
})

export class TooltipDirective implements OnDestroy {

  private componentRef: ComponentRef<TooltipComponent>;
  
  constructor (
    private el: ElementRef,
    private renderer: Renderer2,
    private injector: Injector,
    private resolver: ComponentFactoryResolver,
    private vcr: ViewContainerRef
  ) {}
  
  @Input() relative: boolean;
  @Input() content: string; // Content to display
  @Input('ident') id: string; // Identifier, used partially for checking whether the tooltip is being clicked on
  // This system works nicely for my specific setup because I only have to (and will always) supply the ident
  // and the content will be grabbed by the help icon
  
  @HostListener('click')
  clickInside() {
    if (this.componentRef) {
      return;
    }
    const factory = this.resolver.resolveComponentFactory(TooltipComponent);
    const injector = ReflectiveInjector.resolveAndCreate([
      {
        provide: 'tooltipConfig',
        useValue: {host: this.el.nativeElement}
      }
    ]);
    this.componentRef = this.vcr.createComponent(factory, 0, injector, this.generateText());
  }
  
  @HostListener('document:click', ['$event.target'])
  clickOutside(target) {
    let blur: boolean; // determine whether the tooltip or its native element are out of focus
    if (target.attributes['data-ident']) {
      // ...then we know we're clicking on a tooltip, so now check if it's `this` one
      blur = target.attributes['data-ident'].value === this.el.nativeElement.attributes['ident'].value;
    } else {
      // ...we're just clicking anywhere on the document, so check if it's on the icon that launched this
      blur = this.el.nativeElement.contains(target);
    }
    if (!blur) {
      // get rid of the tooltip if not clicked anywhere near it
      this.destroy();
    }
  }
  
  generateText() {
    // Transcribe the content text to the to-be-generated HTML
    return [[this.renderer.createText(this.content)]];
  }
  
  ngOnDestroy() {
    this.destroy();
  }
  
  destroy() {
    if (this.componentRef) {
      this.componentRef.destroy();
    }
    this.componentRef = null;
  }

}

