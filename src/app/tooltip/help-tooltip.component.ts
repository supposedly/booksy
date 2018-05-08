// A small encircled question mark that serves as a quick-help of sorts
// Pops up with both a brief and a link to the full help page pertaining to whatever feature
import {
  Component,
  OnInit,
  Input,
  HostListener,
  ElementRef
} from '@angular/core';
import { HelpService } from '../help.service';

@Component({
    // tslint:disable-next-line:component-selector
    selector: 'whatsthis',
    template: `
      <div>
        <span
          class="owo"
          (click)="showLink=true"
          tooltip [content]="content" [attr.ident]="ident" [attr.relative]="!absolute"
        ></span>
        <span
          class="link"
          [attr.data-ident]="ident"
          [class.visible]="showLink"
        >
          <a
            [routerLink]="linkUrl"
          >{{linkText}}</a>
        </span>
      </div>
    `,
    styleUrls: ['./help-tooltip.component.css']
})

// The (?)-looking icon that launches a help tooltip.
export class HelpTooltipComponent implements OnInit {
    @Input() ident: string;
    @Input('relative') absolute = true;
    @Input('newtab') inplace = true; // open in place == not in a new tab
    // `absolute` and `inplace` are input as the opposite of what they should be;
    // this is so I can write <tag ... relative> instead of <tag ... relative="meaningless value that evals to truthy">.
    // This way, if the tag *doesn't* contain the name `relative`, the variable `absolute` will be set to `true`
    // and if the tag *does* contain the name `relative` without a value, `absolute` will be undefined (which is falsey).
    showLink = false;
    linkText: string;
    linkUrl: string;
    content: string;
  
  constructor(
    private elementRef: ElementRef,
    private helpService: HelpService
  ) {}
  
  ngOnInit() {
    this.linkUrl = `/help/${this.ident}`;
    this.helpService.getBrief(this.ident)
      .subscribe(resp => { this.linkText = resp.help.title; this.content = resp.help.brief; });
  }
  
  @HostListener('document:click', ['$event.target'])
  determineLinkVisibility(target) {
    // Like in tooltip.directive, check if user is clicking outside of this element's bounds
    // and if they are then hide the element
    this.showLink = this.elementRef.nativeElement.contains(target);
  }
}
